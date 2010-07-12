require "classes"

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/dbneo'

 # jpl_hours = Asset.new :url => "http://jplewicke.com/hours"
 # sg_hours = Asset.new :url => "http://silviogesell.com/hours"
#  hg_hours = Asset.new :url => "http://henrygeorge.com/hours"
#  pp_hours = Asset.new :url => "http://spiderman.com/hours"

  
  def find_asset(name, i)
    begin
      Neo4j::Transaction.run do
        puts "Find all assets with URL #{name}"
        result = Asset.find(:url => name)

        puts "Found #{result.size} assets"
        result.each {|x| puts "#{x.neo_id}\t#{x}"}
        result.each do |x|
          x.sought_by_rels.each {|r| puts "#{r.start_node.quantity} #{r.start_node.offering.url} are offered in exchange for #{x.url}." }
        end
      end
    rescue  
      i = 0
      retry
    end
    return 1
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


threads = []

3.times { |j|
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