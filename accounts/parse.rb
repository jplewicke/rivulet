require "sinatra"
require "neo_classes"
require "json"

# All OpenTransact asset manipulation functions should include the following fields:
# to = a valid user identifier
# amount = a numeric amount of an asset to transfer
# They can also include a memo field, which is a string giving the reason for a
# transaction.
def parses!(params)
  if params["to"] == nil
    throw(:halt, [400, "\"to\" field required by OpenTransact protocol\n"])
  end
  
  if params["amount"] == nil
    throw(:halt, [400, "\"amount\" field required by OpenTransact protocol\n"])
  end
  
  unless numeric?(params["amount"])
    throw(:halt, [400, "\"amount\" field must be a number in OpenTransact\n"])
  end
  
  params["amount"] = Float(params["amount"])
end


def numeric?(str)
  true if Float(str) rescue false
end