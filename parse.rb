require "neo_classes"
require "json"

# All OpenTransact asset manipulation functions should include the following fields:
# to = a valid user identifier
# amount = a numeric amount of an asset to transfer
# They can also include a memo field, which is a string giving the reason for a
# transaction.
def parses!(params)
  if params["to"] == nil
    throw(:halt, [400, "\"to\" field required by OpenTransact protocol.\n"])
  end
  
  if params["amount"] == nil
    throw(:halt, [400, "\"amount\" field required by OpenTransact protocol.\n"])
  end
  
  unless numeric?(params["amount"])
    throw(:halt, [400, "\"amount\" field must be a number in OpenTransact.\n"])
  end
  
  unless Float(params["amount"]) > 0.0
    throw(:halt, [400, "\"amount\" field must be greater than 0 in OpenTransact.\n"])
  end
  
  params["amount"] = Float(params["amount"])
end


def get_neo_users(source_id, dest_id) 
  #One cannot grant credit to oneself.
  if source_id == dest_id
    throw(:halt, [400, "Cannot grant credit to oneself.\n"])
  end
  
  source = User.fromid(source_id)
  dest = User.fromid(dest_id)
  
  if (source == nil || dest == nil)
      throw(:halt, [400, "Error finding user in Neo4j.\n"])
  end
  return [source, dest]
end

def numeric?(str)
  true if Float(str) rescue false
end

def posinteger?(str)
  if Integer(str) > 0  
    true
  else 
    false 
  end
  rescue 
    false
end