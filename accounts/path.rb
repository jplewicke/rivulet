require 'app_classes'
require 'set'
require 'benchmark'


def path_to_credits(users_path)
  if users_path == nil
    return []
  else
    return users_path.each_cons(2).collect {|pair| CreditRelationship.new(pair.first, pair.last)}
  end
end



num_nodes = 200

users = []

Neo4j::Transaction.run do
  num_nodes.times do |i|
    users[i] = User.fromid("User_#{i}")
  end
end

def find_all(num1, num2, users)
  Neo4j::Transaction.run do
    path = []
    b = 0.0
    3.times do
      path = users[num1].traverse.outgoing(:activelytrusts).depth(18).path_to(users[num2])
      
      credits = path_to_credits(path)
    
      max_transfer = credits.collect {|a| a.slack_givable}.min
      
      
      puts " +++++++++"
    
      credits.each do |c| 
        puts ""
        puts c
        c.give!(max_transfer)
        puts c
        c.save!
        puts c
      end
    
      puts max_transfer
      puts " ---------++++++"
      
      
      puts "____________________________________________________________"
    end
    return path.to_a
  end
end

tot = 0.0
reps = 100
times = {}
counts = {}
res = 0

20.times do |i|
  counts[i] = 0
  times[i] = 0.0
end



reps.times do |i|
  puts "Pass #%d" % (i + 1)
  time = Benchmark.realtime do
    i = rand(num_nodes) 
    j = (i + 1) % num_nodes
    res = find_all(i,j, users)
  end
  counts[res.length] += 1
  times[res.length] += time
  tot += time
  
end
puts ""

return

return
puts "Average time:"
puts tot / reps
puts ""

20.times do |i|
  puts "Length #{i}: #{times[i] / counts[i]}"
end

20.times do |i|
  puts "Count of length #{i}: #{counts[i]}"
end