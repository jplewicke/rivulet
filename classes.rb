require "neo4j"

class Offer
  include Neo4j::NodeMixin
  
  # Define Neo4j properties.
  property :created, :oauth_token, :user_id, :quantity
  
  # Define Neo4j relationships.
  has_one :seeking, :offering
  
  # Index some of the node properties using Lucene.
  index :created, :oauth_token, :user_id
end

class Item
  include Neo4j::NodeMixin
  
  # Each item being traded is tracked by an OpenTransact-compatible URL.
  property :url
  
  # Multiple offers can refer to a given item type.
  has_n :seeking, :offering
  
  # Lucene indices.
  index :url
end