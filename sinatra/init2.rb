require "classes"




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

num_nodes = 100000
num_edges = 20

asset_urls = []
num_nodes.times do |i|
  asset_urls[i] = "Asset_#{i}$"
end

assets = []

Neo4j::Transaction.run do
  assets = asset_urls.collect {|a| Asset.new :url => a}
end


  

a = assets.sort_by { rand }
len = assets.length
num_nodes.times do |j|
  puts j
  Neo4j::Transaction.run do
    if j % 20 == 0
      a = assets.sort_by { rand } 
    end
    num_edges.times do |i|
        k = rand(num_nodes - num_edges * 2 - 2)
        s = a[i + k]
        o = a[i + k + 1]
        while (s == o)
          o = a[rand(10)]
        end
        new_offer = Offer.new :quantity => rand(40) + 1
        new_offer.seeking = s
        new_offer.offering = o
        new_offer.offering.rels.outgoing(:tradable_for) << new_offer
        new_offer.rels.outgoing(:tradable_for) << s
    end
  end
end
