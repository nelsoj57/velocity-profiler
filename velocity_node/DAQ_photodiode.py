class DaqAI: ...


class DaqAI_Manager: ...


# TODO: for continous sampling, I will use a callback event like: https://github.com/mjablons1/nidaqmx-continuous-analog-io/blob/main/nidaqxm_2ch_reader_writer.py
# THEN, in the callback function, will read many samples into a preallocated numpy array of size equal to the number of samples needed to triger the callback
# by doing: classnidaqmx.stream_readers.AnalogSingleChannelReader.read_many_sample(...)
# THen in the same callback function, there will be two options:
# 1. if Samples are being done for a specific duration, then an effiecent approach is taken:
# instead of copying data from one place to another, we preallocate a large numpy array equal to the number of total samples we expect to read for the entire duration
# and instead of passing the preallocated array to the read_many_sample function, we pass a slice/view of the preallocated array
# We move the starting index of the slice each time we read samples, so that we can keep appending to the same array

# 2. if an unknown total number of samples will be read, then we probably will just need to copy stuff from the buffer every time we read samples and append it to a list of arrays
# OR we could do a hybrid approach where we preallocate a large array and pass slices and only copy the data to the list of arrays when the buffer is full (BAD IDEA)
# OR (GOOD IDEA) we use a (possibly circular) deque that can store multiple number of frames worth of data and have two threads working on it: consumer and producer model
# - we use a multiprocessing.Queue that can store multiple number of frames worth of data and have two processes working on it: consumer and producer model
# OR (Best IDEA) we just pass in a new preallocated array into the read_many_sample function each time we read samples, and then append the new array to the list of arrays
# - this could be done in a hybrid approach where we preallocate a large buffer and pass slices of it to the read_many_sample def name(args):
# creating a new array only if a buffer is going to be overfilled.
