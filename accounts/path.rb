require 'app_classes'
require 'set'
require 'benchmark'

def find_user(id)
ret = nil
  Neo4j::Transaction.run do
    result = User.find(:user_id => id)
    result.each {|x| ret = x}
  end
return ret
end

def path_to_credits(users_path)
  if users_path == nil
    return []
  else
    return users_path.each_cons(2).collect {|pair| CreditRelationship.new(pair.first, pair.last)}
  end
end

def credit_format(c)
  return "#{c.source.user_id} to #{c.dest.user_id}: \t#{c.slack_givable} fr,\t #{c.slack_returnable} ra \t #{c.source.activelytrusts.include?(c.dest)} \t #{c.dest.activelytrusts.include?(c.source)}"
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
      #puts "start"
      path = users[num1].traverse.outgoing(:activelytrusts).depth(18).path_to(users[num2])
      #puts res.collect {|u| u.user_id}
      credits = path_to_credits(path)
    
      max_transfer = credits.collect {|a| a.slack_givable}.min
      
      #b += max_transfer
      
      puts " +++++++++"
      #puts credits.collect {|a| credit_format(a)}
    
      #puts credits
    
      credits.each do |c| 
        puts ""
        puts credit_format(c)
        c.give!(max_transfer)
        puts credit_format(c)
        c.save!
        puts credit_format(c)
      end
    
      puts max_transfer
    #  puts b
      puts " ---------++++++"
      
      #puts credits.collect {|a| credit_format(a)}
      
      
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