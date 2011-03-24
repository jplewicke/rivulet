require 'neo_classes'
require 'json'

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
      @source.rels(:activelytrusts).outgoing.find {|r| r.getEndNode == @dest}.delete
    end
    if (not @source.activelytrusts.include?(@dest) and self.slack_givable > 0.0)
      @source.activelytrusts << @dest
    end
    if (@dest.activelytrusts.include?(@source) and self.slack_returnable <= 0.0)
      @dest.rels(:activelytrusts).outgoing.find {|r| r.getEndNode == @source}.delete
    end
    if (not @dest.activelytrusts.include?(@source) and self.slack_returnable > 0.0)
      @dest.activelytrusts << @source
    end
    
    
    [@source_offer,@dest_offer].each do |o|
      if o.empty?
        #o.del
        #TODO: commented out since this causes problems with output after saving.
        
      end
    end
  end
  
  def empty?
    [@source_offer,@dest_offer].all? { |o| o.empty? }
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
  
  #Updates the amount @source is offering to @dest to be at least amount,
  #and then debits that amount to @dest as a held balance.
  def hold!(amount)
    @source_offer.amount_held += amount
  end
  
  def to_s
    return "#{@source.user_id} to #{@dest.user_id}: \t#{self.slack_givable} fr, \t #{self.slack_returnable} ra \t #{self.dest_offer.amount_held} dh \t #{self.source_offer.amount_held} sh \t #{@source.activelytrusts.include?(@dest)} \t #{@dest.activelytrusts.include?(@source)}"
  end
  
  def to_json
     return {
       :from => @source.user_id,
       :to => @dest.user_id,
       :credit_accepted => @source_offer.max_desired,
       :credit_offered => @source_offer.max_offered,
       :debit_accepted => @dest_offer.max_desired,
       :debit_offered => @dest_offer.max_offered,
       :max_credit_line => self.slack_givable,
       :max_debit_line => self.slack_returnable,
       :credit_held => self.source_offer.amount_held,
       :debit_held => self.dest_offer.amount_held,
       :net_owed => (self.source_offer.amount_used - self.dest_offer.amount_used) }.to_json
  end
end


class CreditPath
  attr_accessor :source, :dest, :depth, :users, :credits, :debit
  
  #Accepts either a User Neo4j object, or the user ID for a given user.
  def initialize(source, dest)
    #puts "Source #{source}, s.c=#{source.class}\tDest #{dest}, d.c=#{dest.class}"
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
    @debit = CreditRelationship.new(@dest,@source)
  end
  
  #Update paths.
  def refresh!
    puts @users
    @users = Neo4j::Algo.shortest_path(@source,@dest).outgoing(:activelytrusts)
    @users = [] if @users.nil?
    puts @users.public_methods
    begin
      @credits = @users.each_cons(2).collect {|pair| CreditRelationship.new(pair.first, pair.last)}
    rescue NoMethodError
      @users = []
      @credits = []
    end
      
  end
  
  def save!
    @credits.each {|c| c.save!}
    @debit.save!
    #puts @credits
    #puts @debit
  end
  
  #Maximum amount transferable over current path.
  def transferable
    amount = @credits.collect {|c| c.slack_givable}.min
    amount = 0.0 if amount.nil?
    return amount
  end
  
  #Uses current path to transfer an incremental amount to dest.
  def transfer_once!(amount)
    if amount > self.transferable
      raise "Excessive amount being transferred."
    end
    
    @credits.each do |c| 
      #puts c
      c.give!(amount)
    end
    #puts @debit
    @debit.hold!(amount)
    #puts "Number of credits: #{@credits.length}"
  end
  
  #Attempts to transfer the given amount, broken up over several incremental paths.
  #In effect, this resembles the Edmonds-Karp BFS max-flow algorithm, but with
  #early stopping once a certain amount is transferred.
  #It returns the amount transferred, so that the transaction containing a call
  #to this can be rolled back if an insufficient amount is transferred.
  def transfer!(amount)
    
    self.refresh!
    
    amount_transferred = 0.0
    while(self.transferable > 0.0 and amount_transferred < amount)
      to_transfer = [self.transferable, amount - amount_transferred].min
      self.transfer_once!(to_transfer)
      amount_transferred += to_transfer
      self.save!
      self.refresh!
      
      #puts "Transferred #{amount_transferred}"
    end
    #puts "Can transfer #{self.transferable}"
    
    return amount_transferred
  end
  
  def transfer_rollback!(to_transfer,t)
    amount = self.transfer!(to_transfer)

    rel = CreditRelationship.new(@source, @dest)

    #Roll back on failure.
    if amount < to_transfer || rel.dest_offer.amount_held < to_transfer
      t.failure
      throw(:halt, [403, "Insufficient number of credits to transfer.\n"])
    end
    
    [amount,rel]
  end
  
end
  