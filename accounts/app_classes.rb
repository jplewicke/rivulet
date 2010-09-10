require 'neo_classes'
require 'neo4j/extensions/graph_algo'
require 'neo4j/extensions/find_path'

#Various classes that provide an abstract way of managing the flow of credit between
#a source and a destination user.  

#The CreditRelationship class tracks the direct credit that two users have placed in
#each other, such as the credit limits in place and the stock of credit between the two. 

#The CreditPath class tracks the indirect credit present between two users via a
#chain of trusted intermediaries.  A CreditPath thus consists of a number of 
#CreditRelationships that are strung together in a network of trust. Since the 
#availability of intermediate nodes may fluctuate over time, a CreditPath
#is inherently volatile. 


class CreditRelationship
  attr_accessor :source, :dest, :source_offer, :dest_offer
  
  def initialize(source, dest)
    @source = source
    @dest = dest
    
    @source_offer = @source.trustrel(@dest)
    @dest_offer = @dest.trustrel(@source)
  end
  
  # How much more can dest draw from source?
  def slack_givable
    return @source_offer.usable + @dest_offer.amount_used
  end
  
  # How much more can source draw from dest?
  def slack_returnable
    return @dest_offer.usable + @source_offer.amount_used
  end
  
  
  
  #Deletes dummy :trusts relationships that we created and resets the 
  #:activelytrusts flag in both directions.
  def save!()
    
    #Kind of ugly at the moment -- TODO cleanup. 
    
    if (@source.activelytrusts.include?(@dest) and self.slack_givable <= 0.0)
      @source.rels.outgoing(:activelytrusts)[@dest].delete
    end
    if (not @source.activelytrusts.include?(@dest) and self.slack_givable > 0.0)
      @source.activelytrusts << @dest
    end
    if (@dest.activelytrusts.include?(@source) and self.slack_returnable <= 0.0)
      @dest.rels.outgoing(:activelytrusts)[@source].delete
    end
    if (not @dest.activelytrusts.include?(@source) and self.slack_returnable > 0.0)
      @dest.activelytrusts << @source
    end
    
    
    [@source_offer,@dest_offer].each do |o|
      if o.empty?
        o.del
        
      end
    end
  end
  
  #Transfers amount from @source to @dest.
  
  def give!(amount)
    
    if self.slack_givable < amount
      raise "Cannot transfer amount."
    end
    
    debt_to_use = [amount, @dest_offer.amount_used].min
    credit_to_use = [0, amount - debt_to_use].max
    
    @dest_offer.amount_used -= debt_to_use
    @source_offer.amount_used += credit_to_use
  end
  
  def to_s
    return %"#{@source.user_id} to #{@dest.user_id}: \t#{self.slack_givable} fr,\t #{self.slack_returnable} ra \t #{@source.activelytrusts.include?(@dest)} \t #{@dest.activelytrusts.include?(@source)}"
  end
end


class CreditPath
  attr_accessor :source, :dest, :depth, :users, :credits
  
  #Accepts either a User Neo4j object, or the user ID for a given user.
  def initialize(source, dest)
    puts "Source #{source}, s.c=#{source.class}\tDest #{dest}, d.c=#{dest.class}"
    if source.class == User
      @source = source
    else
      @source = User.fromid(source)
    end
    
    if dest.class == User
      @dest = dest
    else
      @dest = User.fromid(dest)
    end
    
    @depth = @source.depth
    @users = []
    @credits = []
  end
  
  #Update paths.
  def refresh!
    puts "Depth #{@depth}"
    @users = @source.traverse.outgoing(:activelytrusts).depth(@depth).path_to(@dest)
    
    @users = [] if @users.nil?
    
    @credits = @users.each_cons(2).collect {|pair| CreditRelationship.new(pair.first, pair.last)}
  end
  
  def save!
    @credits.each {|c| c.save!}
    puts @credits
  end
  
  def transferable
    @credits.collect {|c| c.slack_givable}.min
  end
  
  def transfer!(amount)
    @credits.each do |c| 
      puts ""
      puts c
      c.give!(amount)
      puts c
    end
  end
end
  