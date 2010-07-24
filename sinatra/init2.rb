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




asset_urls = ["jplewicke", 
  "silviogesell",
  "henrygeorge",
  "spiderman",
  "batman",
  "robin",
  "joker",
  "catwoman",
  "patrickhenry",
  "aynrand",
  "johnstossel",
  "robertpaine",
  "rogersherman",
  "johnhancock",
  "oliverwolcott",
  "johnpenn",
  "lymanhall",
  "josiahbartlett",
  "georgewashington",
  "thomasjefferson",
  "samadams",
  "benfranklin"]
  
25000.times do |i|
  asset_urls[i] = "Asset_#{i}$"
end

assets = []

Neo4j::Transaction.run do
  assets = asset_urls.collect {|a| Asset.new :url => a }
end

50.times do |j|
  puts j
  Neo4j::Transaction.run do
    25000.times do |i|
        new_offer = Offer.new :quantity => rand(40) + 1
        j = rand(assets.size - 400)
        k = j + rand(500) - 300
        s = assets[j]
        o = s
        o = assets[k + rand(3)] until o != s
        new_offer.seeking = s
        new_offer.offering = o
    end
  end
end
