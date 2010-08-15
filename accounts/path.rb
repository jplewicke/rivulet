require 'classes'
require 'set'
require 'benchmark'
#require 'Neo4j'
require 'neo4j/extensions/graph_algo'
require 'neo4j/extensions/find_path'

def find_user(id)
ret = nil
  Neo4j::Transaction.run do
    result = User.find(:user_id => id)
    result.each {|x| ret = x}
  end
return ret
end

def path_to_credits(users_path)
  users_path.each_cons(2).collect {|pair| pair.first.rels.outgoing(:trusts)[pair.last]}
end



num_nodes = 500

users = []

Neo4j::Transaction.run do
  num_nodes.times do |i|
    users[i] = find_user("User_#{i}")
  end
end

def find_all(num1, num2, users)
  Neo4j::Transaction.run do
    #puts "start"
    res = users[num1].traverse.outgoing(:trusts).depth(13).path_to(users[num2])
    #puts res.collect {|u| u.user_id}
    #puts path_to_credits(res)
    #puts path_to_credits(res).collect {|r| r.credit_limit }
    return res.to_a
  end
end

tot = 0.0
reps = 1
times = {}
counts = {}
res = 0

20.times do |i|
  counts[i] = 0
  times[i] = 0.0
end

reps.times do |i|
  puts i
  time = Benchmark.realtime do
    i = rand(num_nodes) 
    j = (i + 1) % num_nodes
    res = find_all(i,j, users)
  end
  counts[res.length] += 1
  times[res.length] += time
  tot += time
  
end

puts "Average time:"
puts tot / reps
puts ""

20.times do |i|
  puts "Length #{i}: #{times[i] / counts[i]}"
end

20.times do |i|
  puts "Count of length #{i}: #{counts[i]}"
end