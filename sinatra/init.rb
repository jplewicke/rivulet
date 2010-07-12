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


find_asset("http://jplewicke.com/hours")

Neo4j::Transaction.run do
  jpl_hours = Asset.new :url => "http://jplewicke.com/hours"
  sg_hours = Asset.new :url => "http://silviogesell.com/hours"
  hg_hours = Asset.new :url => "http://henrygeorge.com/hours"
  pp_hours = Asset.new :url => "http://spiderman.com/hours"
  bm_hours = Asset.new :url => "http://batman.com/hours"
  rn_hours = Asset.new :url => "http://robin.com/hours"
  jk_hours = Asset.new :url => "http://joker.com/hours"
  gw_hours = Asset.new :url => "http://georgewashington.com/hours"
  tj_hours = Asset.new :url => "http://thomasjefferson.com/hours"
  sa_hours = Asset.new :url => "http://samadams.com/hours"
  bf_hours = Asset.new :url => "http://benfranklin.com/hours"
  
  
  #jpl_seeking_sg = Offer.new :quantity => 20.0
 # jpl_seeking_sg.seeking = sg_hours
#  jpl_seeking_sg.offering = jpl_hours
  
 # hg_sk_pp
  
  
  offer_list = [{:q => 20.0, :s => sg_hours, :o =>jpl_hours},
    {:q => 11.0, :s => sg_hours, :o =>hg_hours},
    {:q => 7.0, :s => sg_hours, :o =>pp_hours},
    {:q => 12.0, :s => jpl_hours, :o =>hg_hours},
    {:q => 40.0, :s => jpl_hours, :o =>pp_hours},
    {:q => 95.0, :s => pp_hours, :o =>hg_hours},
    {:q => 83.0, :s => hg_hours, :o =>pp_hours},
    ]
    
  for o in offer_list do
    new_offer = Offer.new :quantity => o[:q]
    new_offer.seeking = o[:s]
    new_offer.offering = o[:o]
  end
  
  
  
  sg_hours.sought_by_rels.each {|r| puts "#{r.start_node.quantity} #{r.start_node.offering.url} are offered in exchange for #{sg_hours.url}." }
  # for #{r.end_node.quantity} of #{r.end_node.offering.url}
  #puts jpl_seeking_sg.offering.methods
  #puts jpl_hours.methods
end
  

find_asset("http://jplewicke.com/hours")
find_asset("http://silviogesell.com/hours")
find_asset("http://henrygeorge.com/hours")
find_asset("http://spiderman.com/hours")