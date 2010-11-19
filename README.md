# Rivulet

Rivulet is a simple webservice that allows people to pay each other with IOUs and promises, even if the people making a trade don't know or trust each other.  It does this by allowing people to specify which people they individually trust, and by then finding longer chains of mutual trust that connect the payor and the payee.



## Benefits

Rivulet allows website developers to quickly add a digital payment system for their users that is trustworthy and fraud-resistant.  Since 

## Features

Rivulet uses ACID transactions, so payments will either go through completely or fail 

Rivulet is a simple RESTful web service, so it's easy to integrate with 

## Installation

Rivulet runs on the Ruby web framework Sinatra.  Since it uses the Java graph database Neo4j.

## License

Rivulet is available under the GNU Affero General Public License, as seen in the LICENSE file.  Briefly speaking, this means that if you modify this program, you have to make your changes available to anyone who interacts with it over a network. 

If you have a particular application that requires different licensing, please contact John Paul Lewicke at jplewicke@gmail.com .  Rivulet uses the graph database Neo4j, which charges licensing fees for use with closed source code.

## Acknowledgements

Rivulet was substantially inspired Ryan Fugger's Ripple Monetary S