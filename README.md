# Rivulet

Rivulet is a simple webservice that allows people to pay each other with IOUs and promises, even if the people making a trade don't know or trust each other. If you want to pay a stranger, it searches both of your social trust networks for a sequence of mutual acquaintances to vouch for you by extension.

Rivulet is a simplified version of Ryan Fugger's [Ripple Monetary System](http://ripple-project.org "Ripple").  It's intended to be plugged into existing websites, and doesn't support exchange rates, multiple units of account charging interest or demurrage, or ship with much of a user interface.

If you're looking for a simple way for your users to trade babysitting sessions, car rides, books or CDs, or even to replace money, you've found the right github repo.

## Benefits and Features

Rivulet allows website developers to quickly add a **digital payment** system for their users that is trustworthy.  Since users set whom they trust, they feel empowered.  

Rivulet is **hard for people to game**: doing sham transactions or setting up sock-puppets doesn't earn them any more trust from other users.

Rivulet is **spam-resistant**: even if 20,000 spammers set up accounts, they can't steal anything from legitimate users since they'll be disconnected from the main trust network.

Rivulet **scales well**: it can handle simultaneous requests, find trust paths between people with more than 6 degrees of separation, and handle trust networks with tens of thousands of participants.

Rivulet uses **ACID transactions**, so payments will either go through completely or not have any affect.  Simultaneous attempts to pay with the same IOUs won't end up causing double payments or corruption.

Rivulet is a **simple RESTful web service**, so it's easy to integrate with your existing website.  You can keep your existing interface and integrate Rivulet the way you want to. It's based on [OpenTransact](http://opentransact.org "OpenTransact"), the fledgling spec for simple financial transactions.

## Installation

Rivulet runs on the Ruby web framework Sinatra.  Since it uses the Java graph database Neo4j, it requires JRuby.

## License

Rivulet is available under the GNU Affero General Public License, as seen in the LICENSE file.  Briefly speaking, this means that if you modify this program, you have to make your changes available to anyone who interacts with it over a network. 

If you have a particular application that requires different licensing, please contact John Paul Lewicke at jplewicke@gmail.com .  Rivulet uses the graph database Neo4j, which charges licensing fees for use with closed source code.
