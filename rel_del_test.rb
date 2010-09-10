require 'Neo4j'

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dbneotest'
Lucene::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dblucenetest'
Lucene::Config[:store_on_file] = true

class Dot
  include Neo4j::NodeMixin

  property :numid
  index :numid
  
  
  has_n(:line_to)
end


# Create a large, directed clique.  Each node should have an outgoing edge to 
# and an incoming edge from every other node.

num_dots = 6
dots = []

num_dots.times do |i|
  Neo4j::Transaction.run do
    dots[i] = Dot.new :numid => i
  end
end
1.times do
  Neo4j::Transaction.run do
    dots.each do |source|
      dots.each do |dest|
        if source != dest
          #puts "#{source} #{dest}"
          source.line_to << dest
        end
      end
    end
  end
end
     
# Verify outgoing connection to every other node

Neo4j::Transaction.run do
  dots.each do |source|
    dots.each do |dest|
      if (not source.line_to.include?(dest)) and (source != dest)
        puts "unexpectedly missing line from #{source.numid} to #{dest.numid}"
      end
    end
  end
end

     
# Delete outgoing connection to every other node
Neo4j::Transaction.run do
  1.times do
    dots.each do |source|
      dots.each do |dest|
        if(source != dest)
           source.rels.outgoing(:line_to)[dest].delete
        end
      end
    end
  end
  
     
# Verify absence of outgoing connection to every other node

  dots.each do |source|
    dots.each do |dest|
      if (source.line_to.include?(dest)) and (source != dest)
        puts "unexpectedly present line from #{source.numid} to #{dest.numid}"
      end
    end
  end
  
  puts dots[1].line_to.class
end
