require 'Neo4j'
require 'neo4j/extensions/graph_algo'
require 'neo4j/extensions/find_path'
Neo4j::Config[:storage_path] = './dbneotest'
Lucene::Config[:storage_path] = './dblucenetest'

class Dot
  include Neo4j::NodeMixin
  property :numid
  has_n(:line_to)
end


# Create a line of 20 singly connected dots.
#e.g. dots[0] ---line_to--> dots[1] ----line_to-->....---> dots[19]

num_dots = 20
dots = []

num_dots.times do |i|
  Neo4j::Transaction.run do
    dots[i] = Dot.new :numid => i
  end
end

(num_dots - 1).times do |i|
  Neo4j::Transaction.run do
    #puts "Creating Line from #{i} to #{i+1}"
    dots[i].line_to << dots[i+1]
  end
end

Neo4j::Transaction.run do
  # Depth 1 traversal traverses two relationships. => true
  puts dots[0].traverse.outgoing(:line_to).depth(1).path_to(dots[2]).to_a == dots[0..2]
  
  # Depth 1 traversal cannot traverse 3 relationships. => false
  puts dots[0].traverse.outgoing(:line_to).depth(1).path_to(dots[3]) == dots[0..3]
  
  # Depth 2 traversal traverses 4 relationships. => true
  puts dots[0].traverse.outgoing(:line_to).depth(2).path_to(dots[4]).to_a == dots[0..4]
  
  # Depth 2 traversal cannot traverse 5 relationships. => false
  puts dots[0].traverse.outgoing(:line_to).depth(2).path_to(dots[5]) == dots[0..5]
end