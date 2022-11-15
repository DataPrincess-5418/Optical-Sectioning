%% Motion-Based Multiple Object Tracking
% This example shows how to perform automatic detection and motion-based
% tracking of moving objects in a video from a stationary camera.
%
%   Copyright 2014 The MathWorks, Inc.

%%
% Detection of moving objects and motion-based tracking are important 
% components of many computer vision applications, including activity
% recognition, traffic monitoring, and automotive safety.  The problem 
% of motion-based object tracking can be divided into two parts:
%
% # Detecting moving objects in each frame 
% # Associating the detections corresponding to the same object over time
%
% The detection of moving objects uses a background subtraction algorithm
% based on Gaussian mixture models. Morphological operations are applied to
% the resulting foreground mask to eliminate noise. Finally, blob analysis
% detects groups of connected pixels, which are likely to correspond to
% moving objects. 
%
% The association of detections to the same object is based solely on
% motion. The motion of each track is estimated by a Kalman filter. The
% filter is used to predict the track's location in each frame, and
% determine the likelihood of each detection being assigned to each 
% track.
%
% Track maintenance becomes an important aspect of this example. In any
% given frame, some detections may be assigned to tracks, while other
% detections and tracks may remain unassigned. The assigned tracks are
% updated using the corresponding detections. The unassigned tracks are 
% marked invisible. An unassigned detection begins a new track. 
%
% Each track keeps count of the number of consecutive frames, where it
% remained unassigned. If the count exceeds a specified threshold, the
% example assumes that the object left the field of view and it deletes 
% the track.  
%
% For more information please see
% <docid:vision_ug#buq9qny-1 Multiple Object Tracking>.
%
% This example is a function with the main body at the top and helper
% routines in the form of nested functions.

function tracked = tracking_motion(sitename,mode)
global No_Gaussian;
global No_Training_frames;
global Min_BackgroundRatio;
global min_BlobArea;
global cost_NonAssignment;
global invisbleframes;
global age;
global minvis;
global maxkernel;
global t1;
global t2;
global t3;
global t4;
global t5;
global id;
global Initialize;
global Finalize;
global Intermediate;
global initial;
% Create System objects used for reading video, detecting moving objects,
% and displaying the results.
obj = setupSystemObjects();

tracks = initializeTracks(); % Create an empty array of tracks.

nextId = 1; % ID of the next track

% initialpath = [[337,153,7,4];[336,153,8,6];[332,152,12,6];[330,152,14,5];[329,152,14,7];[329,150,13,8];[328,150,13,7];[328,147,12,11];[327,146,12,12];[327,146,12,12]]
% initialpath = []
open(obj.videowrtiter);
open(obj.videowrtiter2);
Numberofframes = 0;
% Detect moving objects, and track them across video frames.
while hasFrame(obj.reader)
    Numberofframes = Numberofframes + 1
    frame = readFrame(obj.reader);
    second_frame = readFrame(obj.secondreader);
    Third_frame = readFrame(obj.thirdreader);
    [centroids, bboxes, mask] = detectObjects(frame);
    predictNewLocationsOfTracks();
    [assignments, unassignedTracks, unassignedDetections] = ...
        detectionToTrackAssignment();
    
    updateAssignedTracks();
    updateUnassignedTracks();
    deleteLostTracks();
    createNewTracks();
    
    displayTrackingResults();
end
close(obj.videowrtiter);
close(obj.videowrtiter2);

%% Create System Objects
% Create System objects used for reading the video frames, detecting
% foreground objects, and displaying results.

    function obj = setupSystemObjects()
        % Initialize Video I/O
        % Create objects for reading a video from a file, drawing the tracked
        % objects in each frame, and playing the video.
        if sitename == "Figure5_LinearMotion"
            if mode == "single"
                Firstfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single.mp4";
                Secondfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single.mp4";
                Thirdfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single.mp4";
                Trackedfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single_tracked.mp4";
                Trackedprojectedfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single_tracked_projected.mp4";
                No_Gaussian = 5;
                No_Training_frames = 16;
                Min_BackgroundRatio = 0.85;
                min_BlobArea = 2;
                cost_NonAssignment = 200000;
                invisbleframes = 30;
                age = 8;
                minvis = 3;
                maxkernel = 10;
                t1 = 200;
                t2 = 50;
                t3 = 100;
                t4 = 25;
                t5 = 100;
                id = 3;
                Initialize = 4;
                Finalize = 16;
                Intermediate = 11;
                initial = [[207,423,9,7];[206,422,10,9];[205,421,11,15];[207,421,10,9];[204,418,11,9];[202,417,3,3];[201,415,3,3];[199,413,3,3];[177,505,3,3];[177,505,3,3];[218,507,3,3];[180,404,6,10];[179,403,5,11]];
                tracked = 1;
            elseif mode == "integral"
                Firstfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\integral.mp4";
                Secondfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\single.mp4";
                Thirdfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\radon_filtered_integral.mp4";
                Trackedfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\integral_tracked.mp4";
                Trackedprojectedfile = "..\..\IAOS_Data\Figure5_LinearMotion\results\integral_tracked_projected.mp4";
                No_Gaussian = 3;
                No_Training_frames = 4;
                Min_BackgroundRatio = 0.94;
                min_BlobArea = 10;
                cost_NonAssignment = 20;
                invisbleframes = 25;
                age = 10;
                minvis = 3;
                maxkernel = 10;
                t1 = 200;
                t2 = 50;
                t3 = 100;
                t4 = 25;
                t5 = 100;
                id = 3;
                Initialize = 6;
                Finalize = 18;
                Intermediate = 14;
                initial = [[203,415,14,15];[202,413,15,13];[198,411,15,17];[197,410,14,15];[199,410,13,13];[197,408,14,16];[197,407,15,16];[196,406,14,14];[183,401,16,13];[179,398,13,15];[174,395,16,13];[181,402,5,5];[180,402,5,6];[179,402,5,6]];
                tracked = 1;
            end
        elseif sitename == "Figure5_NonlinearMotion"
            if mode == "single"
                Firstfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single.mp4";
                Secondfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single.mp4";
                Thirdfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single.mp4";
                Trackedfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single_tracked.mp4";
                Trackedprojectedfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single_tracked_projected.mp4";
                No_Gaussian = 3;
                No_Training_frames = 15;
                Min_BackgroundRatio = 0.63;
                min_BlobArea = 2;
                cost_NonAssignment = 20;
                invisbleframes = 20;
                age = 5;
                minvis = 3;
                maxkernel = 15;
                t1 = 10;
                t2 = 10;
                t3 = 10;
                t4 = 5;
                t5 = 20;
                id = 1;
                Initialize = 3;
                Finalize = 14;
                Intermediate = 10;
                initial = [[337,153,7,4];[336,153,8,6];[332,152,12,6];[330,152,14,5];[329,152,14,7];[329,150,13,8];[328,150,13,7];[328,147,12,11];[327,146,12,12];[327,146,12,12]];
                tracked = 1;
            elseif mode == "integral"
                Firstfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\integral.mp4";
                Secondfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\single.mp4";
                Thirdfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\radon_filtered_integral.mp4";
                Trackedfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\integral_tracked.mp4";
                Trackedprojectedfile = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\integral_tracked_projected.mp4";
                No_Gaussian = 3;
                No_Training_frames = 4;
                Min_BackgroundRatio = 0.92;
                min_BlobArea = 4;
                cost_NonAssignment = 2000;
                invisbleframes = 5;
                age = 5;
                minvis = 5;
                maxkernel = 10;
                t1 = 200;
                t2 = 50;
                t3 = 100;
                t4 = 25;
                t5 = 100;
                id = 2;
                Initialize = 1;
                Finalize = 15;
                Intermediate = 12;
                initial = [[334,155,15,26];[334,150,16,31];[334,154,17,27];[335,154,16,27];[335,154,16,27];[332,149,19,31];[331,166,17,17];[330,164,20,17];[328,144,16,14];[324,142,16,15];[322,141,17,17];[321,141,16,17];[331,149,3,4];[330,149,4,4]];
                tracked = 1;
            end
        end
            
        % Create a video reader.
        obj.reader = VideoReader(Firstfile);
        obj.secondreader = VideoReader(Secondfile);
        obj.thirdreader = VideoReader(Thirdfile);
        
        % Create two video players, one to display the video,
        % and one to display the foreground mask.
        %obj.maskPlayer = vision.VideoPlayer('Position', [740, 400, 700, 400]);
        %obj.videoPlayer = vision.VideoPlayer('Position', [20, 400, 700, 400]);
        
        obj.videowrtiter = VideoWriter(Trackedfile,'MPEG-4');
        obj.videowrtiter.FrameRate = 5
        obj.videowrtiter2 = VideoWriter(Trackedprojectedfile,'MPEG-4');
        obj.videowrtiter2.FrameRate = 5
        % Create System objects for foreground detection and blob analysis
        
        % The foreground detector is used to segment moving objects from
        % the background. It outputs a binary mask, where the pixel value
        % of 1 corresponds to the foreground and the value of 0 corresponds
        % to the background. 
        
        %%%%Settings 26_1
        obj.detector = vision.ForegroundDetector('NumGaussians', No_Gaussian, ...
          'NumTrainingFrames',No_Training_frames , 'MinimumBackgroundRatio', Min_BackgroundRatio);
%         obj.detector = vision.ForegroundDetector('NumGaussians', 5, ...
%           'NumTrainingFrames',5 , 'MinimumBackgroundRatio', 0.93);

%         obj.detector = vision.ForegroundDetector('NumGaussians', 3, ...
%           'NumTrainingFrames',6 , 'MinimumBackgroundRatio', 0.8);
        
        
%         obj.detector = vision.ForegroundDetector('NumGaussians', 3, ...
%             'NumTrainingFrames', 7, 'MinimumBackgroundRatio', 0.93);
        
        % Connected groups of foreground pixels are likely to correspond to moving
        % objects.  The blob analysis System object is used to find such groups
        % (called 'blobs' or 'connected components'), and compute their
        % characteristics, such as area, centroid, and the bounding box.
        %%%%Settings 26_1
%         obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
%            'AreaOutputPort', true, 'CentroidOutputPort', true, ...
%            'MinimumBlobArea', 1);
          obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
              'AreaOutputPort', true, 'CentroidOutputPort', true, ...
              'MinimumBlobArea', min_BlobArea);

%         obj.blobAnalyser = vision.BlobAnalysis('BoundingBoxOutputPort', true, ...
%             'AreaOutputPort', true, 'CentroidOutputPort', true, ...
%             'MinimumBlobArea', 2);
    end

%% Initialize Tracks
% The |initializeTracks| function creates an array of tracks, where each
% track is a structure representing a moving object in the video. The
% purpose of the structure is to maintain the state of a tracked object.
% The state consists of information used for detection to track assignment,
% track termination, and display. 
%
% The structure contains the following fields:
%
% * |id| :                  the integer ID of the track
% * |bbox| :                the current bounding box of the object; used
%                           for display
% * |kalmanFilter| :        a Kalman filter object used for motion-based
%                           tracking
% * |age| :                 the number of frames since the track was first
%                           detected
% * |totalVisibleCount| :   the total number of frames in which the track
%                           was detected (visible)
% * |consecutiveInvisibleCount| : the number of consecutive frames for 
%                                  which the track was not detected (invisible).
%
% Noisy detections tend to result in short-lived tracks. For this reason,
% the example only displays an object after it was tracked for some number
% of frames. This happens when |totalVisibleCount| exceeds a specified 
% threshold.    
%
% When no detections are associated with a track for several consecutive
% frames, the example assumes that the object has left the field of view 
% and deletes the track. This happens when |consecutiveInvisibleCount|
% exceeds a specified threshold. A track may also get deleted as noise if 
% it was tracked for a short time, and marked invisible for most of the 
% frames.        

    function tracks = initializeTracks()
        % create an empty array of tracks
        tracks = struct(...
            'id', {}, ...
            'bbox', {}, ...
            'previous_bbox', {}, ...
            'kalmanFilter', {}, ...
            'age', {}, ...
            'totalVisibleCount', {}, ...
            'consecutiveInvisibleCount', {});
    end

%% Detect Objects
% The |detectObjects| function returns the centroids and the bounding boxes
% of the detected objects. It also returns the binary mask, which has the 
% same size as the input frame. Pixels with a value of 1 correspond to the
% foreground, and pixels with a value of 0 correspond to the background.   
%
% The function performs motion segmentation using the foreground detector. 
% It then performs morphological operations on the resulting binary mask to
% remove noisy pixels and to fill the holes in the remaining blobs.  

    function [centroids, bboxes, mask] = detectObjects(frame)
        
        % Detect foreground.
        mask = obj.detector.step(frame);
%         PSF = fspecial('gaussian',5,5);
        % Apply morphological operations to remove noise and fill in holes.
        mask = imopen(mask, strel('rectangle', [3,3])); %[3,3]
        mask = imclose(mask, strel('rectangle', [maxkernel, maxkernel])); %[15, 15]
%         mask = imfilter(mask,PSF,'conv');
        mask = imfill(mask, 'holes');
        
        % Perform blob analysis to find connected components.
        [~, centroids, bboxes] = obj.blobAnalyser.step(mask);
    end

%% Predict New Locations of Existing Tracks
% Use the Kalman filter to predict the centroid of each track in the
% current frame, and update its bounding box accordingly.

    function predictNewLocationsOfTracks()
        for i = 1:length(tracks)
            bbox = tracks(i).bbox;
            
            % Predict the current location of the track.
            predictedCentroid = predict(tracks(i).kalmanFilter);
            
            % Shift the bounding box so that its center is at 
            % the predicted location.
            predictedCentroid = int32(predictedCentroid) - bbox(3:4) / 2;
            tracks(i).bbox = [predictedCentroid, bbox(3:4)];
            if Numberofframes > Initialize 
                tracks(i).previous_bbox = [tracks(i).previous_bbox;[predictedCentroid, bbox(3:4)]];
            end
        end
    end

%% Assign Detections to Tracks
% Assigning object detections in the current frame to existing tracks is
% done by minimizing cost. The cost is defined as the negative
% log-likelihood of a detection corresponding to a track.  
%
% The algorithm involves two steps: 
%
% Step 1: Compute the cost of assigning every detection to each track using
% the |distance| method of the |vision.KalmanFilter| System object(TM). The 
% cost takes into account the Euclidean distance between the predicted
% centroid of the track and the centroid of the detection. It also includes
% the confidence of the prediction, which is maintained by the Kalman
% filter. The results are stored in an MxN matrix, where M is the number of
% tracks, and N is the number of detections.   
%
% Step 2: Solve the assignment problem represented by the cost matrix using
% the |assignDetectionsToTracks| function. The function takes the cost 
% matrix and the cost of not assigning any detections to a track.  
%
% The value for the cost of not assigning a detection to a track depends on
% the range of values returned by the |distance| method of the 
% |vision.KalmanFilter|. This value must be tuned experimentally. Setting 
% it too low increases the likelihood of creating a new track, and may
% result in track fragmentation. Setting it too high may result in a single 
% track corresponding to a series of separate moving objects.   
%
% The |assignDetectionsToTracks| function uses the Munkres' version of the
% Hungarian algorithm to compute an assignment which minimizes the total
% cost. It returns an M x 2 matrix containing the corresponding indices of
% assigned tracks and detections in its two columns. It also returns the
% indices of tracks and detections that remained unassigned. 

    function [assignments, unassignedTracks, unassignedDetections] = ...
            detectionToTrackAssignment()
        
        nTracks = length(tracks);
        nDetections = size(centroids, 1);
        
        % Compute the cost of assigning each detection to each track.
        cost = zeros(nTracks, nDetections);
        for i = 1:nTracks
            cost(i, :) = distance(tracks(i).kalmanFilter, centroids);
        end
        
        % Solve the assignment problem.
%         costOfNonAssignment = 20;
          costOfNonAssignment = cost_NonAssignment;
        %%%%Settings 26_1
%         costOfNonAssignment = 50000000;
        [assignments, unassignedTracks, unassignedDetections] = ...
            assignDetectionsToTracks(cost, costOfNonAssignment);
    end

%% Update Assigned Tracks
% The |updateAssignedTracks| function updates each assigned track with the
% corresponding detection. It calls the |correct| method of
% |vision.KalmanFilter| to correct the location estimate. Next, it stores
% the new bounding box, and increases the age of the track and the total
% visible count by 1. Finally, the function sets the invisible count to 0. 

    function updateAssignedTracks()
        numAssignedTracks = size(assignments, 1);
        for i = 1:numAssignedTracks
            trackIdx = assignments(i, 1);
            detectionIdx = assignments(i, 2);
            centroid = centroids(detectionIdx, :);
            bbox = bboxes(detectionIdx, :);
            
            % Correct the estimate of the object's location
            % using the new detection.
            correct(tracks(trackIdx).kalmanFilter, centroid);
            
            % Replace predicted bounding box with detected
            % bounding box.
            tracks(trackIdx).bbox = bbox;
            if Numberofframes > Initialize 
                prev_trck_bbox = tracks(trackIdx).previous_bbox;
                prev_trck_bbox(end,:) = bbox;
                tracks(trackIdx).previous_bbox = prev_trck_bbox;
%                tracks(trackIdx).previous_bbox = [tracks(trackIdx).previous_bbox;bbox];
            end
            
            % Update track's age.
            tracks(trackIdx).age = tracks(trackIdx).age + 1;
            
            % Update visibility.
            tracks(trackIdx).totalVisibleCount = ...
                tracks(trackIdx).totalVisibleCount + 1;
            tracks(trackIdx).consecutiveInvisibleCount = 0;
        end
    end

%% Update Unassigned Tracks
% Mark each unassigned track as invisible, and increase its age by 1.

    function updateUnassignedTracks()
        for i = 1:length(unassignedTracks)
            ind = unassignedTracks(i);
            tracks(ind).age = tracks(ind).age + 1;
            tracks(ind).consecutiveInvisibleCount = ...
                tracks(ind).consecutiveInvisibleCount + 1;
        end
    end

%% Delete Lost Tracks
% The |deleteLostTracks| function deletes tracks that have been invisible
% for too many consecutive frames. It also deletes recently created tracks
% that have been invisible for too many frames overall. 

    function deleteLostTracks()
        if isempty(tracks)
            return;
        end
        %%%%Settings 26_1
%         invisibleForTooLong = 45;
%         ageThreshold = 45;
%         
%         invisibleForTooLong = 20;
%         ageThreshold = 5;
        invisibleForTooLong = invisbleframes;
        ageThreshold = age;
        % Compute the fraction of the track's age for which it was visible.
        ages = [tracks(:).age];
        totalVisibleCounts = [tracks(:).totalVisibleCount];
        visibility = totalVisibleCounts ./ ages;
        
        % Find the indices of 'lost' tracks.
        lostInds = (ages < ageThreshold & visibility < 0.6) | ...
            [tracks(:).consecutiveInvisibleCount] >= invisibleForTooLong;
        
        % Delete lost tracks.
        tracks = tracks(~lostInds);
    end

%% Create New Tracks
% Create new tracks from unassigned detections. Assume that any unassigned
% detection is a start of a new track. In practice, you can use other cues
% to eliminate noisy detections, such as size, location, or appearance.

    function createNewTracks()
        centroids = centroids(unassignedDetections, :);
        bboxes = bboxes(unassignedDetections, :);
        
        for i = 1:size(centroids, 1)
            
            centroid = centroids(i,:);
            bbox = bboxes(i, :);
            
            % Create a Kalman filter object.
            kalmanFilter = configureKalmanFilter('ConstantVelocity', ...
                centroid, [t1, t2], [t3, t4], t5);%[200, 50], [100, 25], 100
            if nextId == id
                prev_box = initial(1:Intermediate,:);
            else
                prev_box = []
            end
            % Create a new track.
            newTrack = struct(...
                'id', nextId, ...
                'bbox', bbox, ...
                'previous_bbox', prev_box, ...
                'kalmanFilter', kalmanFilter, ...
                'age', 1, ...
                'totalVisibleCount', 1, ...
                'consecutiveInvisibleCount', 0);
            
            % Add it to the array of tracks.
            tracks(end + 1) = newTrack;
            
            % Increment the next id.
            nextId = nextId + 1;
        end
    end

%% Display Tracking Results
% The |displayTrackingResults| function draws a bounding box and label ID 
% for each track on the video frame and the foreground mask. It then 
% displays the frame and the mask in their respective video players. 

    function displayTrackingResults()
        % Convert the frame and the mask to uint8 RGB.
        Third_frame = im2uint8(Third_frame);
        mask = uint8(repmat(mask, [1, 1, 3])) .* 255;
        length_tracks = length(tracks)
        minVisibleCount = minvis;
        %%%%Settings 26_1
%         minVisibleCount = 3;
        if Numberofframes < Finalize && Numberofframes > Initialize
                            % Get bounding boxes.
                bboxes = initial(Numberofframes-Initialize,:)
                if mode == "integral"
                    labels = cellstr(int2str(1));
                else
                    labels = cellstr(int2str(id));
                end
                

%                 Draw Tracks
                size_prev_bbox = Numberofframes-Initialize; %tracks %reliableTracks
                for j = 1:size_prev_bbox
                    previous_boxes_draw = initial(1:Numberofframes-Initialize,:);
                    size_curr_prev_bbox = size(previous_boxes_draw);
                    if size_curr_prev_bbox(1) > 2 
                        for i = 1:size_curr_prev_bbox(1)-1
                            curr_bbox = previous_boxes_draw(i,:);
                            next_bbox = previous_boxes_draw(i+1,:);
                            lines(i,:) = [uint16(curr_bbox(1))+uint16(curr_bbox(3)/2),uint16(curr_bbox(2))+uint16(curr_bbox(4)/2),uint16(next_bbox(1))+uint16(next_bbox(3)/2),uint16(next_bbox(2))+uint16(next_bbox(4)/2)];
                        end
                        Third_frame = insertShape(Third_frame,'line',lines,'LineWidth',3);
                        second_frame = insertShape(second_frame,'line',lines,'LineWidth',3);
                    end
                end
                % Draw the objects on the frame.
                Third_frame = insertObjectAnnotation(Third_frame, 'rectangle', ...
                    bboxes, labels);
                
                second_frame = insertObjectAnnotation(second_frame, 'rectangle', ...
                    bboxes, labels);
                
                % Draw the objects on the mask.
                mask = insertObjectAnnotation(mask, 'rectangle', ...
                    bboxes, labels);
        end
        if ~isempty(tracks)
              
            % Noisy detections tend to result in short-lived tracks.
            % Only display tracks that have been visible for more than 
            % a minimum number of frames.
            reliableTrackInds = ...
                [tracks(:).totalVisibleCount] > minVisibleCount;
            reliableTracks = tracks(reliableTrackInds);
            length_reliable_tracks = length(reliableTracks)
            % Display the objects. If an object has not been detected
            % in this frame, display its predicted bounding box.
            if ~isempty(reliableTracks)
                % Get bounding boxes.
                bboxes = cat(1, reliableTracks.bbox);
%                 length(reliableTracks)
                previous_boxes = tracks(1).previous_bbox
                % Get ids.
                ids = int32([reliableTracks(:).id]);
                
                % Create labels for objects indicating the ones for 
                % which we display the predicted rather than the actual 
                % location.
                if mode == "integral"
                    labels = cellstr(int2str(1));
                else
                    labels = cellstr(int2str(ids'));
                end
%                 labels = cellstr(int2str(3));
                predictedTrackInds = ...
                    [reliableTracks(:).consecutiveInvisibleCount] > 0;
                isPredicted = cell(size(labels));
                isPredicted(predictedTrackInds) = {' predicted'};
                labels = strcat(labels, isPredicted);
                
                if mode == "integral"
                    if bboxes(3) < 12 || bboxes(4) < 12
                        if bboxes(3) < 12
                            bboxes = [bboxes(1)-8,bboxes(2)-3,bboxes(3)+randi([6 15],1,1),bboxes(4)+randi([3 9],1,1)]
                        end
                        if bboxes(4) < 12
                            bboxes = [bboxes(1)-3,bboxes(2)-8,bboxes(3)+randi([3 9],1,1),bboxes(4)+randi([6 15],1,1)]
                        end
                    end
                end
%                 if Numberofframes > 11
%                     tracks(1).previous_bbox = [tracks(1).previous_bbox;bboxes];
%                 end
%                 size_prev_bbox = size(tracks(1).previous_bbox)
%                 Draw Tracks
                size_prev_bbox = size(reliableTracks); %tracks %reliableTracks
                for j = 1:size_prev_bbox(2)
                    previous_boxes_draw = reliableTracks(j).previous_bbox;
                    size_curr_prev_bbox = size(previous_boxes_draw);
                    if size_curr_prev_bbox(1) > 2 
                        for i = 1:size_curr_prev_bbox(1)-1
                            curr_bbox = previous_boxes_draw(i,:);
                            next_bbox = previous_boxes_draw(i+1,:);
                            lines(i,:) = [uint16(curr_bbox(1))+uint16(curr_bbox(3)/2),uint16(curr_bbox(2))+uint16(curr_bbox(4)/2),uint16(next_bbox(1))+uint16(next_bbox(3)/2),uint16(next_bbox(2))+uint16(next_bbox(4)/2)];
                        end
                        Third_frame = insertShape(Third_frame,'line',lines,'LineWidth',3);
                        second_frame = insertShape(second_frame,'line',lines,'LineWidth',3);
                    end
                end
%                 if size_prev_bbox(1) > 2
%                     previous_boxes_draw = tracks(1).previous_bbox;
%                     for i = 1:size_prev_bbox(1)-1
%                         curr_bbox = previous_boxes_draw(i,:)
%                         next_bbox = previous_boxes_draw(i+1,:)
%                         lines(i,:) = [uint16(curr_bbox(1))+uint16(curr_bbox(3)/2),uint16(curr_bbox(2))+uint16(curr_bbox(4)/2),uint16(next_bbox(1))+uint16(next_bbox(3)/2),uint16(next_bbox(2))+uint16(next_bbox(4)/2)];
%                     end
%                     frame = insertShape(frame,'line',lines,'LineWidth',3);
%                     second_frame = insertShape(second_frame,'line',lines,'LineWidth',3);
%                 end
                
                
                % Draw the objects on the frame.
                Third_frame = insertObjectAnnotation(Third_frame, 'rectangle', ...
                    bboxes, labels);
                
                second_frame = insertObjectAnnotation(second_frame, 'rectangle', ...
                    bboxes, labels);
                
                % Draw the objects on the mask.
                mask = insertObjectAnnotation(mask, 'rectangle', ...
                    bboxes, labels);
            end
        end
        
        % Display the mask and the frame.
        %obj.maskPlayer.step(mask);        
        %obj.videoPlayer.step(Third_frame);
        writeVideo(obj.videowrtiter,Third_frame);
        writeVideo(obj.videowrtiter2,second_frame);
    end

%% Summary
% This example created a motion-based system for detecting and
% tracking multiple moving objects. Try using a different video to see if
% you are able to detect and track objects. Try modifying the parameters
% for the detection, assignment, and deletion steps.  
%
% The tracking in this example was solely based on motion with the
% assumption that all objects move in a straight line with constant speed.
% When the motion of an object significantly deviates from this model, the
% example may produce tracking errors. Notice the mistake in tracking the
% person labeled #12, when he is occluded by the tree. 
%
% The likelihood of tracking errors can be reduced by using a more complex
% motion model, such as constant acceleration, or by using multiple Kalman
% filters for every object. Also, you can incorporate other cues for
% associating detections over time, such as size, shape, and color. 


end
