import traceback
import code
import os

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate
from tqdm import tqdm

import config

PLOT = False


def rank_features(query_scores):
    i = 0
    scores = []
    for vid_name, feature_scores in query_scores.items():
        try:
            labels = feature_scores.keys()
            # weights = np.asarray([FEATURE_WEIGHTS.get(label, 1.0)
            #   for label in labels])
            lens = [len(feature_scores[i]) for i in labels]
            max_len = max(lens)
            # max_len = max([len(i) for i in combined_scores])

            y = np.asarray([np.append(np.asarray(feature_scores[label]), np.zeros(max_len - lens[idx]))
                            * config.FEATURE_WEIGHTS.get(label, config.DEFAULT_WEIGHT) for idx, label in enumerate(labels) if config.FEATURE_WEIGHTS.get(label, config.DEFAULT_WEIGHT) > 0])
            Y = np.sum(y, axis=0)

            scores.append((vid_name, np.max(Y), y, Y, [
                          label for label in labels if config.FEATURE_WEIGHTS.get(label, config.DEFAULT_WEIGHT) > 0]))
        except:
            traceback.print_exc()
            code.interact(local=locals())

    final_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return final_scores


def generate_plot(score):

    Y = score[3]
    f = plt.figure()
    ax = plt.Axes(f, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.plot(range(Y.shape[0]), Y, linewidth=3)
    f.add_axes(ax)
    # f.tight_layout()
    f.canvas.draw()

    data = np.fromstring(f.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(f.canvas.get_width_height()[::-1] + (3,))

    h, w, _ = data.shape
    for i in range(w):
        if np.any(data[:, i, :]):
            left_lim = i
            break

    for i in range(1, 1+w):
        if np.any(data[:, -i, :]):
            right_lim = -i
            break

    data = data[:, left_lim:right_lim, :]
    data = np.copy(data)

    # f.close()

    return data


def generate_plots(final_scores, title, save_location=None):
    [print(x[:2]) for x in final_scores]
    stack_ylim = max([np.max(score[3]) for score in final_scores])
    for i, score in enumerate(final_scores):
        vid_name = score[0]
        y = score[2]
        Y = score[3]
        labels = score[4]
        colors = [config.FEATURE_COLORS[label] for label in labels]

        plt.figure(title+'_stacked', figsize=(12, 12))
        plt.plot(range(Y.shape[0]), Y, label=vid_name)

        plt.figure(title+'_comparison', figsize=(12, 12))
        plt.subplot(3, 3, i + 1)
        plt.ylim(0, stack_ylim)
        plt.xticks([])
        plt.stackplot(range(y.shape[1]), y, labels=labels, colors=colors)
        plt.title(vid_name)

    plt.figure(title+'_stacked')
    plt.legend()
    plt.title(title)
    if save_location is not None:
        plt.savefig(os.path.join(save_location, title+'_stacked.png'), dpi=600)

    f = plt.figure(title+'_comparison')
    f.tight_layout()
    axarr = plt.subplot(3, 3, 9)
    s = plt.stackplot(range(y.shape[1]), np.zeros(
        y.shape), labels=labels, colors=colors)
    axarr.set_axis_off()
    f.subplots_adjust(top=0.9)
    f.suptitle(title)
    plt.legend(labels, ncol=2)

    for group in s:
        group.set_visible(False)

    if save_location is not None:
        plt.savefig(os.path.join(save_location,
                                 title+'_comparison.png'), dpi=600)
    # plt.show()


def compare_features(query_vid_obj, db_vid_obj):

    ccoeff = {}

    for key in query_vid_obj.features.keys():
        # print('Comparing', key)
        q = query_vid_obj.features[key]
        d = db_vid_obj.features[key]
        if 'brightness' in key:
            ccoeff[key] = similarity_score(q, d)

        if 'perceptual_hash' in key:
            ccoeff[key] = similarity_score(q, d, '2d_hamm')

        if 'blockmotion' in key:
            ccoeff[key] = similarity_score(q, d, '2d_norm')

        if 'audio_spectral_profile' in key:
            ccoeff[key] = similarity_score(q, d, '2d_spectral')

    return ccoeff


def similarity_score(x, y, method='1d_norm'):
    window_size = x.shape[0]
    sim_metric_len = y.shape[0] - window_size

    sim_metric = np.zeros(sim_metric_len)

    if method == '1d_norm':
        # Compute 1D sliding window metric with normalized correlation
        X = x - np.mean(x)
        # X = X / np.max(np.abs(X))
        for start in range(0, sim_metric_len):

            Y = y[start:start+window_size] - \
                np.mean(y[start:start+window_size])

            # Y = Y / np.max(np.abs(Y))

            sim_metric[start] = np.sum(
                X*Y) / np.sqrt(np.sum(X**2) * np.sum(Y**2))

        sim_metric = (sim_metric - np.min(sim_metric))

    elif method == '2d_norm':
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
            print('Error in 2d_norm')
            traceback.print_exc()
            code.interact(local=locals())

    elif method == '2d_spectral':
        # Compute 2D sliding window metric with normalized correlation, for each row individually
        try:
            X = x - np.expand_dims(np.mean(x, axis=1), axis=1)
            X = X / np.max(np.abs(X))
            for start in range(0, sim_metric_len):

                Y = y[start:start+window_size, :] - \
                    np.expand_dims(
                        np.mean(y[start:start+window_size, :], axis=1), axis=1)

                Y = Y / np.max(np.abs(Y))

                # code.interact(local=locals())
                # sim_metric[start] = np.mean([
                #     np.corrcoef(X[i, :], Y[i, :]) for i in range(X.shape[0])
                # ]
                # )
                sim_metric[start] = np.mean(
                    np.sum(X*Y, axis=1) /
                    np.sqrt(np.sum(X**2, axis=1) * np.sum(Y**2, axis=1))
                )

            sim_metric = (sim_metric - np.min(sim_metric))
            # plt.plot(sim_metric)
            # plt.show()
            # code.interact(local=locals())
            # print(sim_metric)
        except:
            print('Error in 2d_spectral')
            traceback.print_exc()
            code.interact(local=locals())

    elif method == '2d_hamm':
        # Compute 2D sliding window metric with hamming distance
        try:
            X = x - np.mean(x)
            for start in range(0, sim_metric_len):

                Y = y[start:start+window_size, :, :] - \
                    np.mean(y[start:start+window_size, :, :])

                sim_metric[start] = 1/(1+hamming_distance(X, Y))

            sim_metric = (sim_metric - np.min(sim_metric))
        except:
            print('Error in 2d_hamm')
            traceback.print_exc()
            code.interact(local=locals())

    return sim_metric


def hamming_distance(x, y):
    return np.sum(x != y)
