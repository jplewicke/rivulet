require "classes"
require 'neo4j/extensions/find_path'


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
jpl_hours = find_asset(asset_urls[1])

#Find shortest-link way to trade sg_hours for jpl_hours.


Neo4j::Transaction.run do
  path = sg_hours.traverse.both(:offered_by,:seeking,:offering,:sought_by).depth(:all).path_to(jpl_hours)
  
  print exchange_path(path)
  puts path.class
  puts path.length
  puts path.nil?

  puts sg_hours.rels
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