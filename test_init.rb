require "app_classes"

num_nodes = 500
num_edges_per = 15


user_ids = []
num_nodes.times do |i|
  user_ids[i] = "User_#{i}"
end

users = []

Neo4j::Transaction.run do
  users = user_ids.collect {|a| User.new :user_id => a, :depth => 15, :secret => "pw"}
  puts users
end


  

a = users.sort_by { rand }
num_nodes.times do |j|
  len = users.length
  puts j
  Neo4j::Transaction.run do
    if j % 20 == 0
      a = users.sort_by { rand }
    end
    num_edges_per.times do |i|
        k = rand(num_nodes - num_edges_per * 2 - 2)
        dest = a[i + k]
        source = a[i + k + 1]
        while (dest == source)
          source = a[rand(10)]
        end
        
        rel = CreditRelationship.new(source, dest)
        source_offer = rel.source_offer
        source_offer.max_offered += 1.0
        source_offer.max_desired += 1.0
        
        rel.save!()
    end
  end
end
