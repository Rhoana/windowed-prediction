import numpy as np
import theano
import theano.tensor as T
from theano import shared, function
theano.config.floatX = 'float32'
rng = np.random.RandomState(42)

class PreProcess(object):
    
    def __init__(self,train_samples,val_samples,test_samples,load_in=False):
        self.load_in = load_in
        self.train_samples = train_samples
        self.val_samples   = val_samples
        self.test_samples  = test_samples
        
    def run(self):

        if self.load_in == True:
            print 'Error'
            exit()
    
        else:
            import os
            train_set_x = np.load('data/x_train.npy')[:self.train_samples]
            train_set_y = np.load('data/y_train.npy')[:self.train_samples]
            test_set_x  = np.load('data/x_test.npy')[:self.test_samples]
            test_set_y  = np.load('data/y_test.npy')[:self.test_samples]
                
            valid_set_size = self.val_samples
            flip_prob = 0.5
            
            print 'Size of training/test-set: ',self.train_samples,'/',self.test_samples
           
            rand_val = np.random.permutation(range(test_set_x.shape[0]))[:valid_set_size]
            valid_set_x = np.zeros((valid_set_size,train_set_x.shape[1]))
            valid_set_y = np.zeros((valid_set_size,train_set_x.shape[1]))
            for n in xrange(len(rand_val)):
                valid_set_x[n] = test_set_x[rand_val[n]]
                valid_set_y[n] = test_set_y[rand_val[n]]

        #number_flips = np.int(np.floor(train_set_x.shape[1]*flip_prob))
        #rand = np.random.permutation(range(train_set_x.shape[1]))[:number_flips]
        #
        #for n in xrange(rand.size):
        #    train_set_x[rand[n]] = train_set_x[rand[n],::-1]
        #train_set_y[rand[n]] = train_set_y[rand[n],::-1]
            
        # estimate the mean and std dev from the training data
        # then use these estimates to normalize the data
        # estimate the mean and std dev from the training data
        
        norm_mean = train_set_x.mean()
        train_set_x = train_set_x - norm_mean
        norm_std = train_set_x.std()
        norm_std = norm_std.clip(0.00001, norm_std)
        train_set_x = train_set_x / norm_std 

        test_set_x = test_set_x - norm_mean
        test_set_x = test_set_x / norm_std 
        valid_set_x = valid_set_x - norm_mean
        valid_set_x = valid_set_x / norm_std 
        
        train_set_x = train_set_x.astype(np.float32)
        test_set_x = test_set_x.astype(np.float32)
        valid_set_x = valid_set_x.astype(np.float32)

        train_set_y = train_set_y.astype(np.float32)
        test_set_y = test_set_y.astype(np.float32)
        valid_set_y = valid_set_y.astype(np.float32)

        train_set_x = theano.shared(train_set_x,borrow=True)
        valid_set_x = theano.shared(valid_set_x,borrow=True)
        test_set_x = theano.shared(test_set_x,borrow=True)

        train_set_y = theano.shared(train_set_y,borrow=True)
        valid_set_y = theano.shared(valid_set_y,borrow=True)
        test_set_y = theano.shared(test_set_y,borrow=True)
        
        list_it = [train_set_x,valid_set_x,test_set_x,train_set_y,valid_set_y,test_set_y]
        
        return list_it

if __name__ == "__main__":
    pre_process =  PreProcess()
    pre_process.run()
    