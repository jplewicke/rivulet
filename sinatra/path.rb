require 'classes'
require 'set'
require 'benchmark'
require 'Neo4j'
require 'neo4j/extensions/graph_algo'
require 'neo4j/extensions/find_path'



Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/dbneo'

def find_asset(name)
ret = nil
  Neo4j::Transaction.run do
  #  puts "Find all assets with URL #{name}"
    result = Asset.find(:url => name)
   result.each {|x| ret = x}
  end
return ret
end

def urls2(enum)
  enum.collect do |n| 
    case n
    when Asset
      "#{n.url}_<asset>"
    when Offer
      "#{n.offering.url}_(offered #{n.quantity})"
    end
  end
end

asset_urls = Array.new
assets = Array.new

Neo4j::Transaction.run do
  100.times do |i|
    asset_urls[i] = "Asset_#{i}$"
    assets[i] = find_asset(asset_urls[i])
  end
end


Neo4j::Transaction.run do
  res = Neo4j::GraphAlgo.all_simple_paths.from(assets[40]).to(assets[43]).depth(13).both("Offer#seeking","Asset#offered_by")
  # asp = org.neo4j.graphalgo.AllSimplePaths.new(assets[0]._java_node, assets[1]._java_node,11)
  #res.each {|p| puts urls2(p.to_a.reverse)}
  
  puts urls2(res.first.to_a.reverse)
#  puts asp.class
  #puts assets[1]._java_node.class
  #puts assets[40].rels.public_methods
  #puts assets[40].rels.class
  puts assets[40].incoming(:all).to_a
  #puts assets[40].traverse.outgoing(:tradable_for).depth(13).path_to(assets[43])
end
