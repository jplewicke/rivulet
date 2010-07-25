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

asset_urls = []
60000.times do |i|
  asset_urls[i] = "Asset_#{i}$"
end

assets = []

Neo4j::Transaction.run do
  assets = asset_urls.collect {|a| Asset.new :url => a}
end


  

480.times do |j|
  puts j
  Neo4j::Transaction.run do
    a = assets.sort_by { rand }
    b = assets.sort_by { rand } 
    5000.times do |i|
        s = a[i]
        o = b[i]
        while (s == o)
          o = b[rand(10)]
        end
        new_offer = Offer.new :quantity => rand(40) + 1
        new_offer.seeking = s
        new_offer.offering = o
        new_offer.offering.rels.outgoing(:tradable_for) << new_offer
        new_offer.rels.outgoing(:tradable_for) << s
    end
  end
end
