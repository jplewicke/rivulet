require "sinatra"
require "json"

require "app_classes"
require "auth"
require "parse"

get '/accounts/:payor/?' do |payor|
  Neo4j::Transaction.run do |t|
    auth_list = [payor]
    protected!(auth_list)
    {:user => authed_user(auth_list), :depth => User.fromid(authed_user(auth_list)).depth}.to_json
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
      user = User.new :user_id => params["user"], :depth => depth, :secret => params["secret"]
      
      {:user => user.user_id, :depth => user.depth}.to_json
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

    puts rel.to_json
    puts "\n"
    rel.to_json
  end
end

post '/transactions/:payor/?' do |payor|
  Neo4j::Transaction.run do |t|
    protected!([payor])
    parses!(params)
    payee = params["to"]
    source, dest = get_neo_users(payor, payee)
    
    #This is an attempt to pay someone other than #{payor} by crediting the payee
    #through the credit network.  Since this will place #{payor} in debt to someone who
    #has extended credit to him/her or will debit an existing credit balance owed to
    ##{payor}, this must be authorized by #{payor}.
  
    #After we parse the request and take care of authorization, we need to make sure 
    #that this operation can be completed in a single Neo4j transaction and that a
    #sufficient number of credits can be transferred.
    
    path = CreditPath.new(source, dest)
    path.depth = source.depth
    to_transfer = params["amount"]
    amount = path.transfer!(to_transfer)

    rel = CreditRelationship.new(source, dest)

    #Roll back on failure.
    if amount < to_transfer || rel.dest_offer.amount_held < to_transfer
      t.failure
      throw(:halt, [403, "Insufficient number of credits to transfer.\n"])
    end
    
    #Since the default method for transferring credits accumulates the resulting credit
    #to the payee as a reserved amount, we need to clear that hold and store this transaction
    #before we can complete it.
    
    rel.dest_offer.amount_held -= to_transfer
    puts rel.to_json
    puts "\n"
    rel.to_json
  end
end

post '/transactions/:payor/held/?' do |payor|
  Neo4j::Transaction.run do |t|
    payee = params["to"]
    protected!([payor, payee])
    parses!(params)
    source, dest = get_neo_users(payor, payee)
    requested_by = authed_user([payor, payee])
    
    #If we can properly authenticate the issuer of this request as either payor or
    #payee, we will accumulate the requested amount of credit from payor to payee
    #by debiting payor's existing credit lines.
    
    path = CreditPath.new(source, dest)
    path.depth = source.depth
    to_transfer = params["amount"]
    amount = path.transfer!(to_transfer)

    rel = CreditRelationship.new(source, dest)

    #Roll back on failure.
    if amount < to_transfer || rel.dest_offer.amount_held < to_transfer
      t.failure
      throw(:halt, [403, "Insufficient number of credits to transfer.\n"])
    end
    
    #Since the default method for transferring credits accumulates the resulting credit
    #to the payee as a reserved amount, we need to clear that hold and store this transaction
    #before we can complete it.
    
    puts rel.to_json
    puts "\n"
    rel.to_json
    
  end
end

post '/transactions/:payor/held/:payee/?' do |payor, payee|
  Neo4j::Transaction.run do |t|
    protected!([payor])
    parses!(params)
    source, dest = get_neo_users(payor, payee)
    
    #Release part of a held credit balance as payment or a gift.
    #Request must have been authorized by payor.
  end
end