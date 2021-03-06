import os
import sys
import time

import numpy

import theano
import theano.tensor as T

from lib import init


class HiddenLayer(object):
    def __init__(self, rng, input, n_in, n_out, W = None, b = None, 
            activation=None, params = {}, params_number = None,maxoutsize = 1):
        """
        Fully connected layer 
        """
        
        # Define input
        self.input = input

        W_name = "W" + str(params_number)
        b_name = "b" + str(params_number)
    
        if W == None or b == None:
            # Initialize weights
            if params.has_key(W_name) and params.has_key(b_name): 
                W = theano.shared(params[W_name], name=W_name, borrow=True)
        
                # Initialize biasea
                b = theano.shared(params[b_name], name=b_name, borrow=True)

            else:
                W_values = numpy.asarray(
                    rng.uniform(
                        low  = -numpy.sqrt(6. / (n_in + n_out)),
                        high = numpy.sqrt(6. / (n_in + n_out)),
                        size = (n_in, n_out)
                    ),
                    dtype=theano.config.floatX
                )

                W = theano.shared(value=W_values, name=W_name, borrow=True)
        
                # Initialize biasea
                b_values = numpy.zeros((n_out,), dtype=theano.config.floatX)
                b = theano.shared(value=b_values, name=b_name, borrow=True)
            
                W = theano.shared(init.HeNormal((n_in, n_out)), borrow=True, name = W_name)
                b = theano.shared(init.constant((n_out,), 0.), borrow=True, name = b_name)

        self.W = W
        self.b = b
        
        # Calculate output 
        output = activation(T.dot(input, self.W) + self.b)
        
        # Maxout                                                                
        maxout_out = None                                                       
        for i in xrange(maxoutsize):                                            
            t = output[:,i::maxoutsize]                                   
            if maxout_out is None:                                              
                maxout_out = t                                                  
            else:                                                               
                maxout_out = T.maximum(maxout_out, t)
                
        self.output = maxout_out

        # Add parameters to model
        self.params = [self.W, self.b]

    def TestVersion(self,rng, input, n_in, n_out, W = None, b = None, 
            activation=None, params = {}, params_number = None,maxoutsize = 1):
        return HiddenLayer(rng, input, n_in, n_out, W = self.W, b = self.b,
                activation = activation, params = params, params_number = params_number,maxoutsize=maxoutsize)


