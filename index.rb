require "app_classes"
require "sinatra"

get '/*' do
  begin
    Neo4j::Transaction.run do |t|
      j = rand(499)
      i = 499 - j
    
      path = CreditPath.new("User_#{i}", "User_#{j}")
      path.depth = 4
      to_transfer = 4.0
      amount = path.transfer!(to_transfer)

      #path.save!
      #Roll back on failure.
      if amount < to_transfer
        puts "FAILED"
        t.failure
      end
    
    
    end
  #rescue NativeException
    #retry
  end
end