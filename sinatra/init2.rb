require "classes"

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/dbneo'



def find_asset(name)
  Neo4j::Transaction.run do
    puts "Find all assets with URL #{name}"
    result = Asset.find(:url => name)

    puts "Found #{result.size} assets"
    result.each {|x| puts "#{x.neo_id}\t#{x}"}
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

Neo4j::Transaction.run do
  
  assets = asset_urls.collect {|a| Asset.new :url => a }
  
  
  #jpl_seeking_sg = Offer.new :quantity => 20.0
 # jpl_seeking_sg.seeking = sg_hours
#  jpl_seeking_sg.offering = jpl_hours
  
 # hg_sk_pp
  
  
  500.times do
    new_offer = Offer.new :quantity => rand(40) + 1
    s = assets[rand(assets.size)]
    o = s
    o = assets[rand(assets.size)] until o != s
    new_offer.seeking = s
    new_offer.offering = o
  end
  
  
  
  #puts jpl_seeking_sg.offering.methods
  #puts jpl_hours.methods
end

