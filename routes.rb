require "rubygems"
require "bundler"
Bundler.setup

require "sinatra"
require "json"

require "app_classes"
require "auth"
require "parse"

get '/' do
  File.read(File.join('public', 'index.html'))
end


get '/accounts/:payor/?' do |payor|
  Neo4j::Transaction.run do |t|
    auth_list = [payor]
    protected!(auth_list)
    User.fromid(payor).to_json
  end
end

# Accepts an option to= parameter for the
get '/credits/:lender/?' do |lender|
  Neo4j::Transaction.run do |t|
    lendee = params["to"]
    if lendee != nil
      auth_list = [lender,lendee]
    else
      auth_list = [lender]
    end
  
    protected!(auth_list)
    requested_by = authed_user(auth_list)
  
    if requested_by == lendee || params["to"] != nil
      source, dest = get_neo_users(lender, lendee)
      CreditRelationship.new(source,dest).to_json
    else
      source = User.fromid(lender)
      puts source.trusts
    end
  end
end


post '/accounts/?' do
  Neo4j::Transaction.run do |t|
    if params["user"] != nil && params["secret"] != nil && User.fromid(params["user"]) == nil
     
      depth = 8
      if params["depth"] != nil && posinteger?(params["depth"])
        depth = Integer(params["depth"])
      end
      
      #Create account for new user.
      user = User.new :user_id => params["user"], :depth => depth, :encrypted_password => BCrypt::Password.create(params["secret"])
      user.to_json
    else
      throw(:halt, [403, "Not authorized\n"])
    end
  end
end

post '/credits/:lender/?' do |lender| 
  Neo4j::Transaction.run do |t|
    lendee = params["to"]
    protected!([lender, lendee])
    parses!(params)
    source, dest = get_neo_users(lender, lendee)
    requested_by = authed_user([lender, lendee])
    
    #If they authenticate as #{lender}, then we parse their request to see to whom 
    #they'd like to extend credit, and how much they'd like to extend.
    
    #If they authenticate as someone else, we make sure they match the user identified
    #in the request.  The lendee allowed to set the maximum amount they'd like to
    #borrow from the lender.
    
    rel = CreditRelationship.new(source, dest)
    source_offer = rel.source_offer
    
    if (lender == requested_by)
      source_offer.max_offered = params["amount"]
    elsif (lendee == requested_by)
      source_offer.max_desired = params["amount"]
    else
      throw(:halt, [500, "Error finding user in Neo4j after authentication.\n"])
    end
    
    #TODO: have it try to reclaim any credit in excess of what is currently possible.
    
    rel.save!()
    {:from => lender, :to => lendee, :credit_offered => source_offer.max_offered, :credit_accepted => source_offer.max_desired}.to_json

    #puts rel.to_json
    #puts "\n"
    rel.to_json
  end
end

post '/transactions/:payor/?' do |payor|
  Neo4j::Transaction.run do |t|
    protected!([payor])
    parses!(params)
    payee = params["to"]
    source, dest = get_neo_users(payee, payor)
    
    #This is an attempt to pay someone other than #{payor} by crediting the payee
    #through the credit network.  Since this will place #{payor} in debt to someone who
    #has extended credit to him/her or will debit an existing credit balance owed to
    ##{payor}, this must be authorized by #{payor}.
  
    #After we parse the request and take care of authorization, we need to make sure 
    #that this operation can be completed in a single Neo4j transaction and that a
    #sufficient number of credits can be transferred.
    
    path = CreditPath.new(source, dest)
    to_transfer = params["amount"]
    amount, rel = path.transfer_rollback!(to_transfer,t)
    
    #Since the default method for transferring credits accumulates the resulting credit
    #to the payee as a reserved amount, we need to clear that hold and store this transaction
    #before we can complete it.
    
    rel.dest_offer.amount_held -= to_transfer
    #puts rel.to_json
    #puts "\n"
    rel.to_json
  end
end

post '/transactions/:payor/held/?' do |payor|
  Neo4j::Transaction.run do |t|
    payee = params["to"]
    protected!([payor, payee])
    parses!(params)
    source, dest = get_neo_users(payee, payor)
    requested_by = authed_user([payor, payee])
    
    #If we can properly authenticate the issuer of this request as either payor or
    #payee, we will accumulate the requested amount of credit from payor to payee
    #by debiting payor's existing credit lines.
    
    path = CreditPath.new(source, dest)
    to_transfer = params["amount"]
    amount, rel = path.transfer_rollback!(to_transfer,t)
    
    #puts rel.to_json
    #puts "\n"
    rel.to_json
  end
end

#Release part of a held credit balance as payment or a gift.
post '/transactions/:payor/held/:payee/?' do |payor, payee|
  Neo4j::Transaction.run do |t|
    protected!([payor])
    parses!(params)
    source, dest = get_neo_users(payee, payor)
    
    rel = CreditRelationship.new(source, dest)
    can_transfer = rel.dest_offer.amount_held
    to_transfer = params["amount"]
    
    if can_transfer < to_transfer
      throw(:halt, [403, "Insufficient reserved balance."])
    else
      rel.dest_offer.amount_held -= to_transfer
      rel.to_json
    end
  end
end

#Should have an option to DELETE a held credit balance.

# Accepts an option to= parameter for the 
get '/transactions/:payor/?' do |payor|
  throw(:halt, [500, "not implemented yet"])
end

get '/transactions/:payor/held/?' do |payor|
  throw(:halt, [500, "not implemented yet"])
end

# Accepts an option to= parameter for the
get '/credits/:payor' do |payor|
  throw(:halt, [500, "not implemented yet"])
end

