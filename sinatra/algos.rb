require 'classes'
require 'set'


Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/dbneo'


  
def find_asset(name)
  ret = nil
#  begin
    Neo4j::Transaction.run do
    #  puts "Find all assets with URL #{name}"
      result = Asset.find(:url => name)
     result.each {|x| ret = x}
    end
#   rescue
#    retry
#   end
  return ret
end

def exchange_path(path)
  return nil if path.nil?

  path.each_index do |i|
    path[i] = case path[i]
      when Asset
        path[i].url
      when Offer
        path[i].quantity
    end
  end
end
  
def url(node)
  case node[:obj]
  when Asset 
    node[:obj].url
  when Offer 
    node[:obj].offering.url
  end
end
    

def seen(node, visited)
  case node[:obj]
  when Asset
    visited.include?(url(node))
  when Offer
    visited.include?(url(node))
  else
    raise "Invalid type in seen. %s" % node[:obj].class
  end
end
  
# Returns a list of 2-tuples of all other assets offered in exchange for the current
# asset, along with the quantity available of them along the best route.
def bfs_step(exploring, visited)
  case exploring[:obj]
  when Asset
    all_offers = exploring[:obj].sought_by.collect { |offer|
      {:obj => offer, :pred => exploring }}
    all_offers.delete_if { |o| seen(o, visited) }
  when Offer
    seen(exploring, visited) ? [] : [{:obj => exploring[:obj].offering, :pred => exploring}]
  else
      raise "Invalid type passed into bfs_step. %s" % exploring[:obj].class
  end
end

def augmenting_path(offered,sought)
  discovered = Set.new [offered.url]
  
  visiting = [{:obj => offered, :pred => nil}]
  
  visiting.each do |node|
    if node[:obj] == sought
      return node
    else
      found = bfs_step(node, discovered)
      discovered = discovered | found.collect {|n| url(n)}
      discovered.each {|url| puts url}
      puts "________________"
      
    end
  end
end
  
asset_urls = ["http://jplewicke.com/hours", 
  "http://silviogesell.com/hours",
  "http://henrygeorge.com/hours",
  "http://spiderman.com/hours",
  "http://batman.com/hours",
  "http://robin.com/hours",
  "http://joker.com/hours",
  "http://catwoman.com/hours",
  "http://patrickhenry.com/hours",
  "http://aynrand.com/hours",
  "http://johnstossel.com/hours",
  "http://robertpaine.com/hours",
  "http://rogersherman.com/hours",
  "http://johnhancock.com/hours",
  "http://oliverwolcott.com/hours",
  "http://johnpenn.com/hours",
  "http://lymanhall.com/hours",
  "http://josiahbartlett.com/hours",
  "http://georgewashington.com/hours",
  "http://thomasjefferson.com/hours",
  "http://samadams.com/hours",
  "http://benfranklin.com/hours"]


# max_flow()


sg_hours = find_asset(asset_urls[1])
jpl_hours = find_asset(asset_urls[0])
jpl_hours2 = find_asset(asset_urls[0])

#Find shortest-link way to trade sg_hours for jpl_hours.


Neo4j::Transaction.run do
  
  puts augmenting_path(sg_hours, jpl_hours)
  
end

return

threads = []

1.times { |j|
  threads << Thread.new(j) { |k|
    i = 1

    for a in asset_urls do
      i = find_asset(a, i)
      puts "Executing thread #{k}, waiting #{i} seconds."
      sleep(i)
    end
    puts "sleeping for 7 seconds at the end"
    sleep(3)
    puts "done sleeping"
    sleep(2)
  }
}

threads.each { |aThread|   aThread.join }