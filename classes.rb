require "neo4j"

class Asset ; end

class Offer
  include Neo4j::NodeMixin
  
  # Define Neo4j properties.
  property :quantity
  
  # Define Neo4j relationships.
  has_one(:seeking).to(Asset, :sought_by)
  has_one(:offering).from(Asset, :offered_by)
  
  # Index some of the node properties using Lucene.
  index :created, :oauth_token, :user_id
end

class Asset
  include Neo4j::NodeMixin
  
  # Each item being traded is tracked by an OpenTransact-compatible URL.
  property :url
  
  # Multiple offers can refer to a given asset 
  has_n(:sought_by).from(Offer, :seeking)
  has_n(:offered_by).to(Offer, :offering)
  
  
  # Lucene indices.
  index :url
end