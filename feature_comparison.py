import code

import numpy as np
import matplotlib.pyplot as plt

import config

PLOT = False


def rank_features(query_scores):
    i = 0
    scores = []
    for vid_name, feature_scores in query_scores.items():
        labels = feature_scores.keys()
        # weights = np.asarray([FEATURE_WEIGHTS.get(label, 1.0)
        #   for label in labels])
        y = np.asarray([np.asarray(feature_scores[i]) *
                        config.FEATURE_WEIGHTS.get(i, config.DEFAULT_WEIGHT) for i in labels])
        Y = np.sum(y, axis=0)

        scores.append((vid_name, np.max(Y), y, Y, labels))

    final_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return final_scores


def generate_plots(final_scores):
    print([x[:2] for x in final_scores])
    for i, score in enumerate(final_scores):
        vid_name = score[0]
        y = score[2]
        Y = score[3]
        labels = score[4]

        plt.figure(1)
        plt.plot(range(Y.shape[0]), Y, label=vid_name)

        plt.figure(2)
        plt.subplot(3, 3, i + 1)
        plt.ylim(0, 2)
        plt.stackplot(range(y.shape[1]), y, labels=labels)
        plt.title(vid_name)

    plt.figure(1)
    plt.legend()
    plt.figure(2)
    plt.subplot(3, 3, 9)
    s = plt.stackplot(range(y.shape[1]), y, labels=labels)
    plt.axes('off')
    plt.legend(labels)

    for group in s:
        group.set_visible(False)

    plt.show()


def compare_features(query_vid_obj, db_vid_obj):

    ccoeff = {}

    for key in query_vid_obj.features.keys():
        # print('Comparing', key)
        q = query_vid_obj.features[key]
        d = db_vid_obj.features[key]
        if 'brightness' in key:
            ccoeff[key] = similarity_score(q, d)

        elif 'perceptual_hash' in key:
            ccoeff[key] = similarity_score(q, d, '2d_hamm')

        elif 'blockmotion' in key:
            ccoeff[key] = similarity_score(q, d, '2d_norm')

    return ccoeff


def similarity_score(x, y, method='1d_norm'):
    window_size = x.shape[0]
    sim_metric_len = y.shape[0] - window_size

    sim_metric = np.zeros(sim_metric_len)

    if method == '1d_norm':
        # Compute 1D sliding window metric with normalized correlation
        X = x - np.mean(x)
        for start in range(0, sim_metric_len):

            Y = y[start:start+window_size] - \
                np.mean(y[start:start+window_size])

            sim_metric[start] = np.sum(
                X*Y) / np.sqrt(np.sum(X**2) * np.sum(Y**2))

        sim_metric = (sim_metric - np.min(sim_metric))

    if method == '2d_norm':
        # Compute 2D sliding window metric with normalized correlation
        try:
            X = x - np.mean(x)
            for start in range(0, sim_metric_len):

                Y = y[start:start+window_size, :, :] - \
                    np.mean(y[start:start+window_size, :, :])

                sim_metric[start] = np.sum(
                    X*Y) / np.sqrt(np.sum(X**2) * np.sum(Y**2))

            sim_metric = (sim_metric - np.min(sim_metric))
        except:
            code.interact(local=locals())

    if method == '2d_hamm':
        # Compute 2D sliding window metric with hamming distance
        try:
            X = x - np.mean(x)
            for start in range(0, sim_metric_len):

                Y = y[start:start+window_size, :, :] - \
                    np.mean(y[start:start+window_size, :, :])

                sim_metric[start] = 1/(1+hamming_distance(X, Y))

            sim_metric = (sim_metric - np.min(sim_metric))
        except:
            code.interact(local=locals())

    return sim_metric


def hamming_distance(x, y):
    return np.sum(x != y)
