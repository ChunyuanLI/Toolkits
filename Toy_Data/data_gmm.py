#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 13:22:00 2017

@author: cli

This code is modified from ALI/datasets

https://github.com/IshmaelBelghazi/ALI/blob/master/ali/datasets.py

"""

import numpy as np
import numpy.random as npr
from scipy.stats import multivariate_normal
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from functools import reduce



class GMM_distribution(object):
    """ Gaussian Mixture Distribution

    Parameters
    ----------
    means : tuple of ndarray.
       Specifies the means for the gaussian components.
    variances : tuple of ndarray.
       Specifies the variances for the gaussian components.
    priors : tuple of ndarray
       Specifies the prior distribution of the components.

    """

    def __init__(self, means=None, variances=None, priors=None, rng=None, seed=None):

        if means is None:
            means = map(lambda x:  10.0 * np.array(x), [[0, 0],
                                                        [1, 1],
                                                        [-1, -1],
                                                        [1, -1],
                                                        [-1, 1]])
        # Number of components
        self.ncomponents = len(means)
        self.dim = means[0].shape[0]
        self.means = means
        # If prior is not specified let prior be flat.
        if priors is None:
            priors = [1.0/self.ncomponents for _ in range(self.ncomponents)]
        self.priors = priors
        # If variances are not specified let variances be identity
        if variances is None:
            variances = [np.eye(self.dim) for _ in range(self.ncomponents)]
        self.variances = variances

        assert len(means) == len(variances), "Mean variances mismatch"
        assert len(variances) == len(priors), "prior mismatch"

        if rng is None:
            rng = npr.RandomState(seed=seed)
        self.rng = rng

    def _sample_prior(self, nsamples):
        return self.rng.choice(a=self.ncomponents,
                               size=(nsamples, ),
                               replace=True,
                               p=self.priors)

    def sample(self, nsamples):
        # Sampling priors
        samples = []
        fathers = self._sample_prior(nsamples=nsamples).tolist()
        for father in fathers:
            samples.append(self._sample_gaussian(self.means[father],
                                                 self.variances[father]))
        return np.array(samples), np.array(fathers)

    def _sample_gaussian(self, mean, variance):
        # sampling unit gaussians
        epsilons = self.rng.normal(size=(self.dim, ))

        return mean + np.linalg.cholesky(variance).dot(epsilons)

    def _gaussian_pdf(self, x, mean, variance):
        return multivariate_normal.pdf(x, mean=mean, cov=variance)

    def pdf(self, x):
        "Evaluates the the probability density function at the given point x"
        pdfs = map(lambda m, v, p: p * self._gaussian_pdf(x, m, v),
                   self.means, self.variances, self.priors)
        return reduce(lambda x, y: x + y, pdfs, 0.0)



class sample_GMM():
    """ Toy dataset containing points sampled from a gaussian mixture distribution.

    The dataset contains 3 sources:
    * samples
    * label
    * densities

    """
    def __init__(self, num_examples, means=None, variances=None, priors=None,
                 **kwargs):
        rng = kwargs.pop('rng', None)
        if rng is None:
            seed = kwargs.pop('seed', 0)
            rng = np.random.RandomState(seed)
    
        gaussian_mixture = GMM_distribution(means=means,
                                                       variances=variances,
                                                       priors=priors,
                                                       rng=rng)
        self.means = gaussian_mixture.means
        self.variances = gaussian_mixture.variances
        self.priors = gaussian_mixture.priors

        features, labels = gaussian_mixture.sample(nsamples=num_examples)
        densities = gaussian_mixture.pdf(x=features)

        data ={'samples': features, 'label': labels, 'density': densities}
        
        self.data = data
        
def plot_GMM(dataset, save_path):
    samples       = dataset.data['samples']
    targets = dataset.data['label']
    X = samples[:, 0], 
    Y = samples[:, 1]
    c_type = cm.nipy_spectral(np.linspace(0, 1, max(targets*2)))
    colors = [c_type[i-1] for i in targets]

    figure, ax = plt.subplots(nrows=1, ncols=1, figsize=(4.5, 4.5))
    ax.set_aspect('equal')
    ax.set_xlim(-4, 4)
    ax.set_ylim([-4, 4])
    ax.set_xticks([-4, -4, -2, 0, 2, 4, 4])
    ax.set_yticks([-4, -4, -2, 0, 2, 4, 4])
    ax.set_xlabel('$x_1$')
    ax.set_ylabel('$x_2$')
    ax.axis('on')
        
    ax.set_title('$\mathbf{x} \sim $GMM$(\mathbf{x})$')
       
    ax.scatter(X, Y, marker='.', c=colors, alpha=0.3, edgecolors='face')   
    plt.tight_layout()
    plt.savefig(save_path, transparent=True, bbox_inches='tight')     
        
def plot_GMM_density(dataset, save_path):

    samples = dataset.data['samples']
    X = samples[:, 0]
    Y = samples[:, 1]
    Z = dataset.data['density']
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    
    ax.plot_trisurf(X, Y, Z, alpha=0.3, cmap=cm.coolwarm, linewidth=0.2 )
   
    ax.set_xlabel('$x_1$')
    ax.set_xlim(np.min(X), np.max(X))
    ax.set_ylabel('$x_2$')
    ax.set_ylim(np.min(Y), np.max(Y))
    ax.set_zlabel('Density')
    ax.set_zlim(0, max(Z))
    plt.tight_layout()
    plt.savefig(save_path, transparent=True, bbox_inches='tight')     

    
    
if __name__ == '__main__':
    means = map(lambda x:  np.array(x), [[0, 0],
                                     [2, 2],
                                     [-1, -1],
                                     [1, -1],
                                     [-1, 1]])
    means = list(means)
    std = 0.1
    variances = [np.eye(2) * std for _ in means]
                 
    priors = [1.0/len(means) for _ in means]   
              
    gaussian_mixture = GMM_distribution(means=means,
                                                   variances=variances,
                                                   priors=priors)
    dataset = sample_GMM(1000, means, variances, priors, sources=('features', )) 
    save_sample_path = 'results/gmm_samples.pdf'
    plot_GMM(dataset, save_sample_path)
    
    save_density_path = 'results/gmm_density.pdf'
    plot_GMM_density(dataset, save_density_path)


                