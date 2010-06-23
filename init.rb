require "classes"

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/dbneo'

Neo4j::Transaction.run do
  jpl_hours = Asset.new :url => "http://jplewicke.com/hours"
  sg_hours = Asset.new :url => "http://silviogesell.com/hours"
  hg_hours = Asset.new :url => "http://henrygeorge.com/hours"
  
  jpl_seeking_sg = Offer.new :quantity => 20.0
  jpl_seeking_sg.seeking = sg_hours
  jpl_seeking_sg.offering = jpl_hours
  
  
  
  
  sg_hours.sought_by_rels.each {|r| puts "#{r.start_node.quantity} #{r.start_node.offering.url} are offered in exchange for #{sg_hours.url}." }
  # for #{r.end_node.quantity} of #{r.end_node.offering.url}
  #puts jpl_seeking_sg.offering.methods
  #puts jpl_hours.methods
end
  
  
  
  def find_actor(name)
    Neo4j::Transaction.run do
      puts "Find all actors named #{name}"
      result = Asset.find(:url => name)

      puts "Found #{result.size} actors"
      result.each {|x| puts "#{x.neo_id}\t#{x}"}
    end
  end
  find_actor("http://silviogesell.com/hours")