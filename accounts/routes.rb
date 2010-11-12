require "app_classes"
require "sinatra"

get '/accounts' do
  #Returns account information for all accounts.
end

post '/accounts' do
  #Create account for new user.
end

post '/credits/:name' do |name|
  #Someone is attempting to change a credit line extended by #{name}.
  
  #If they authenticate as #{name}, then we parse their request to see to whom 
  #they'd like to extend credit, and how much they'd like to.
  
  #If they authenticate as someone else, we make sure they match the user identified
  #in the request.  Other users are allowed to set the maximum amount they'd like to
  #borrow from #{name}.
end

post '/transactions/:payor' do |payor|
  #This is an attempt to pay someone other than #{payor} by crediting the payee
  #through the credit network.  Since this will place #{payor} in debt to someone who
  #has extended credit to him/her or will debit an existing credit balance owed to
  ##{payor}, this must be authorized by #{payor}.
  
  #For now, we are only doing basic HTTP auth instead of OAuth.  Thus the request
  #must authenticate as #{payor}.
  
  #After we parse the request and take care of authorization, we need to make sure 
  #that this operation can be completed in a single Neo4j transaction and that a
  #sufficient number of credits can be transferred.
  
  #Since the default method for transferring credits accumulates the resulting credit
  #to the payee as a reserved amount, we need to clear that hold and store this transaction
  #before we can complete it.
end

get '/transactions/:payor/held' do |payor|
  #to=payee&amount=amount
  #If we can properly authenticate the issuer of this request as either payor or
  #payee, we will accumulate the requested amount of credit from payor to payee
  #by debiting payor's existing credit lines.
  
end

get '/transactions/:payor/held/:payee' do |payor, payee|
  #Release part of a held credit balance as payment or a gift.
  #Request must have been authorized by payor.
end