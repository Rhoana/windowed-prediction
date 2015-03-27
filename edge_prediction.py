import sys
import time as time
import os
import numpy as np
import theano
import theano.tensor as T
from util.pre_process                  import PreProcess 
from data.read_img                     import * 
from edge_prediction_conv.edge_cov_net import CovNet 

def process_cmd_line_args():
    
    if len(sys.argv) > 1 and ( "--pre-process" in sys.argv):
        print "Generating Train/Test Set..."
        generate_training_set()
        print "Finished Train/Test Set..."
        if ((sys.argv).index("--pre-process") + 1) < len(sys.argv):
            if sys.argv[((sys.argv).index("--pre-process") + 1)] == "only":
                sys.exit()

    if len(sys.argv) > 1 and ( "--small" in sys.argv):
        num_kernels   = [10,10,10]
        kernel_sizes  = [(5, 5), (3, 3), (3,3)]
        train_samples = 1500
        val_samples   = 200
        test_samples  = 500
    elif len(sys.argv) > 1 and ( "--medium" in sys.argv):
        num_kernels  = [64,64,64]
        kernel_sizes = [(5, 5), (3, 3), (3,3)]
        train_samples = 4000
        val_samples   = 200
        test_samples  = 1000
    elif len(sys.argv) > 1 and ( "--large" in sys.argv):
        num_kernels  = [80,80,80]
        kernel_sizes = [(5, 5), (3, 3), (3,3)]
        train_samples = 9000
        val_samples   = 200
        test_samples  = 1000
    else:
        print 'Error: pass network size (small/medium/large)'
        exit()

    return num_kernels, kernel_sizes, train_samples, val_samples, test_samples

def run(rng=np.random.RandomState(42),
        net_size = 'small',
        batch_size   = 50,
        epochs       = 100,
        optimizer    = 'RMSprop',
        optimizerData = {},
        in_window_shape = (48,48),
        out_window_shape = (48,48)
        ):
    
    ##### PROCESS COMMAND-LINE ARGS #####
    num_kernels, kernel_sizes, train_samples, val_samples, test_samples = process_cmd_line_args()

    print 'Loading data ...'
    
    # load in and process data
    preProcess              = PreProcess(train_samples,val_samples,test_samples)
    data                    = preProcess.run()
    train_set_x,train_set_y = data[0],data[3]
    valid_set_x,valid_set_y = data[1],data[4]
    test_set_x,test_set_y   = data[2],data[5]

    print 'Initializing neural network ...'

    # print error if batch size is to large
    if valid_set_y.eval().size<batch_size:
        print 'Error: Batch size is larger than size of validation set.'

    # compute batch sizes for train/test/validation
    n_train_batches  = train_set_x.get_value(borrow=True).shape[0]
    n_test_batches   = test_set_x.get_value(borrow=True).shape[0]
    n_valid_batches  = valid_set_x.get_value(borrow=True).shape[0]
    n_train_batches /= batch_size
    n_test_batches  /= batch_size
    n_valid_batches /= batch_size

    # symbolic variables
    x = T.matrix('x')  # input image data
    y = T.matrix('y')  # input label data
    
    cov_net = CovNet(rng, batch_size, num_kernels, kernel_sizes, x, y)

    # Initialize parameters and functions
    cost   = cov_net.layer4.negative_log_likelihood(y)        # Cost function
    params = cov_net.params                                   # List of parameters
    grads  = T.grad(cost, params)                          # Gradient
    index  = T.lscalar()                                   # Index
    
    # Intialize optimizer
    updates = cov_net.init_optimizer(optimizer, cost, params, optimizerData)

    # Training model
    train_model = theano.function(
                  [index],
                  cost,
                  updates = updates,
                  givens  = {
                            x: train_set_x[index * batch_size: (index + 1) * batch_size], 
                            y: train_set_y[index * batch_size: (index + 1) * batch_size] 
        }
    )

    #Validation function
    validate_model = theano.function(
                     [index],
                     cov_net.layer4.errors(y),
                     givens = {
                              x: valid_set_x[index * batch_size: (index + 1) * batch_size],
                              y: valid_set_y[index * batch_size: (index + 1) * batch_size]
            }
        )

    #Test function
    test_model = theano.function(
                 [index],
                 cov_net.layer4.errors(y),
                 givens = {
                          x: test_set_x[index * batch_size: (index + 1) * batch_size],
                          y: test_set_y[index * batch_size: (index + 1) * batch_size]
        }
    )

    
    # Solver
    try:
        print '... Solving'
        start_time = time.time()    
        for epoch in range(epochs):
            t1 = time.time()
            costs             = [train_model(i) for i in xrange(n_train_batches)]
            validation_losses = [validate_model(i) for i in xrange(n_valid_batches)]
            t2 = time.time()
            print "Epoch {}    NLL {:.2}    %err in validation set {:.1%}    Time (epoch/total) {:.2}/{:.2} mins".format(epoch + 1, np.mean(costs), np.mean(validation_losses),(t2-t1)/60.,(t2-start_time)/60.)
    except KeyboardInterrupt:
        print 'Exiting solver ...'
    #Evaluate performance 
    test_errors = [test_model(i) for i in range(n_test_batches)]
    print "test errors: {:.1%}".format(np.mean(test_errors))
    
    predict = theano.function(inputs=[index], 
                                outputs=cov_net.layer4.prediction(),
                                givens = {
                                    x: test_set_x[index * batch_size: (index + 1) * batch_size]
                                    }
                                )
                                
    # Plot example of output
    output = np.zeros((0,out_window_shape[0]*out_window_shape[1]))
    for i in xrange(n_test_batches):
        output = np.vstack((output,predict(i)))
    
    in_shape = (output.shape[0],in_window_shape[0],in_window_shape[1])
    out_shape = (output.shape[0],out_window_shape[0],out_window_shape[1])

    output = output.reshape(out_shape)

    if not os.path.exists('results'):
        os.makedirs('results')
    
    np.save('results/output.npy',output)
    np.save('results/x.npy',test_set_x.eval().reshape(in_shape))
    np.save('results/y.npy',test_set_y.eval().reshape(in_shape))

if __name__ == "__main__":
    
    # GLOBAL CONFIG
    theano.config.floatX = 'float32'
    
    optimizerData = {}
    optimizerData['learning_rate'] = 0.001
    optimizerData['rho']           = 0.9
    optimizerData['epsilon']       = 1e-4

    rng = np.random.RandomState(42)

    run(rng=rng, optimizerData=optimizerData)
    
    
    
    
    
    
    
