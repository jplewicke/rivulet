require 'app_classes'
require 'benchmark'




num_nodes = 200

users = []

Neo4j::Transaction.run do
  num_nodes.times do |i|
    users[i] = User.fromid("User_#{i}")
  end
end

def find_all(num1, num2, list)
  path = []
  users = []
  b = 0.0
  1.times do
    Neo4j::Transaction.run do |t|
      path = CreditPath.new(list[num1], list[num2])
      
      path.depth = 4
      path.refresh!
      users = path.users
      
      
      puts " +++++++++"
      to_transfer = path.transferable
      to_transfer = 1.0
      amount = path.transfer!(to_transfer)
      
      path.save!
      #Roll back on failure.
      if amount < to_transfer
        puts "FAILED"
        t.failure
      end
    end
  
    puts " ---------++++++"
    Neo4j::Transaction.run do |t|
      puts users.to_a.collect {|u| u.user_id}
    end
    
    puts "____________________________________________________________"
    
  end
  return users.to_a
end

tot = 0.0
reps = 100
times = {}
counts = {}
res = 0

200.times do |i|
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

puts "Average time:"
puts tot / reps
puts ""

8.times do |i|
  puts "Length #{i}: #{times[i] / counts[i]}"
end

9.times do |i|
  puts "Count of length #{i}: #{counts[i]}"
end