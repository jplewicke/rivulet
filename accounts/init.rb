require "classes"

num_nodes = 200
num_edges_per = 10


user_ids = []
num_nodes.times do |i|
  user_ids[i] = "User_#{i}"
end

users = []

Neo4j::Transaction.run do
  users = user_ids.collect {|a| User.new :user_id => a}
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
        s = a[i + k]
        o = a[i + k + 1]
        while (s == o)
          o = a[rand(10)]
        end
        rel = o.trusts.new(s)
        rel.max_credit_offered = rand(10) + 1
        rel.max_credit_desired = rand(10) + 1
        rel.credit_used = 0
    end
  end
end
