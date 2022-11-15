function video_written =  write_IAOS_videos(sitename)
if sitename == "Figure5_LinearMotion"
    Processedd_site = "Figure5_LinearMotion"
    single_images_folder = "..\..\IAOS_Data\Figure5_LinearMotion\images";
    integral_images_folder = "..\..\IAOS_Data\Figure5_LinearMotion\results\integral";
    radon_filtered = "..\..\IAOS_Data\Figure5_LinearMotion\results\radon_filtered";
    workingDir = '..\..\IAOS_Data\Figure5_LinearMotion\results';
    %%
    single_imageNames = dir(fullfile(single_images_folder,'*.png'));
    single_imageNames_unsorted = {single_imageNames.name}';
    [~,single_imageNames]=sort_nat(single_imageNames_unsorted);
    single_outputVideo = VideoWriter(fullfile(workingDir,'single.mp4'),'MPEG-4');
    single_outputVideo.FrameRate = 5;
    open(single_outputVideo)
    for ii = 1:length(single_imageNames)
        img = imread(fullfile(single_images_folder,single_imageNames_unsorted{single_imageNames(ii)}));
        writeVideo(single_outputVideo,img)
    end
    close(single_outputVideo)
    %%
    integral_imageNames = dir(fullfile(integral_images_folder,'*.png'));
    integral_imageNames_unsorted = {integral_imageNames.name}';
    [~,integral_imageNames]=sort_nat(integral_imageNames_unsorted);
    integral_outputVideo = VideoWriter(fullfile(workingDir,'integral.mp4'),'MPEG-4');
    integral_outputVideo.FrameRate = 5;
    open(integral_outputVideo)
    for ii = 1:length(integral_imageNames)
        img = imread(fullfile(integral_images_folder,integral_imageNames_unsorted{integral_imageNames(ii)}));
        writeVideo(integral_outputVideo,img)
    end
    close(integral_outputVideo)
    %%
    radon_imageNames = dir(fullfile(radon_filtered,'*.png'));
    radon_imageNames_unsorted = {radon_imageNames.name}';
    [~,radon_imageNames]=sort_nat(radon_imageNames_unsorted);
    radon_outputVideo = VideoWriter(fullfile(workingDir,'radon_filtered_integral.mp4'),'MPEG-4');
    radon_outputVideo.FrameRate = 5;
    open(radon_outputVideo)
    for ii = 1:length(radon_imageNames)
        img = imread(fullfile(radon_filtered,radon_imageNames_unsorted{radon_imageNames(ii)}));
        writeVideo(radon_outputVideo,img)
    end
    close(radon_outputVideo)
    video_written = 0;
elseif sitename == "Figure5_NonlinearMotion"
   Processedd_site = "Figure5_NonlinearMotion" 
    single_images_folder = "..\..\IAOS_Data\Figure5_NonlinearMotion\images";
    integral_images_folder = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\integral";
    radon_filtered = "..\..\IAOS_Data\Figure5_NonlinearMotion\results\radon_filtered";
    workingDir = '..\..\IAOS_Data\Figure5_NonlinearMotion\results';
    %%
    single_imageNames = dir(fullfile(single_images_folder,'*.png'));
    single_imageNames_unsorted = {single_imageNames.name}';
    [~,single_imageNames]=sort_nat(single_imageNames_unsorted);
    single_outputVideo = VideoWriter(fullfile(workingDir,'single.mp4'),'MPEG-4');
    single_outputVideo.FrameRate = 5;
    open(single_outputVideo)
    for ii = 1:length(single_imageNames)
        img = imread(fullfile(single_images_folder,single_imageNames_unsorted{single_imageNames(ii)}));
        writeVideo(single_outputVideo,img)
    end
    close(single_outputVideo)
    %%
    integral_imageNames = dir(fullfile(integral_images_folder,'*.png'));
    integral_imageNames_unsorted = {integral_imageNames.name}';
    [~,integral_imageNames]=sort_nat(integral_imageNames_unsorted);
    integral_outputVideo = VideoWriter(fullfile(workingDir,'integral.mp4'),'MPEG-4');
    integral_outputVideo.FrameRate = 5;
    open(integral_outputVideo)
    for ii = 1:length(integral_imageNames)
        img = imread(fullfile(integral_images_folder,integral_imageNames_unsorted{integral_imageNames(ii)}));
        writeVideo(integral_outputVideo,img)
    end
    close(integral_outputVideo)
    %%
    radon_imageNames = dir(fullfile(radon_filtered,'*.png'));
    radon_imageNames_unsorted = {radon_imageNames.name}';
    [~,radon_imageNames]=sort_nat(radon_imageNames_unsorted);
    radon_outputVideo = VideoWriter(fullfile(workingDir,'radon_filtered_integral.mp4'),'MPEG-4');
    radon_outputVideo.FrameRate = 5;
    open(radon_outputVideo)
    for ii = 1:length(radon_imageNames)
        img = imread(fullfile(radon_filtered,radon_imageNames_unsorted{radon_imageNames(ii)}));
        writeVideo(radon_outputVideo,img)
    end
    close(radon_outputVideo)
    video_written = 0;
else
    video_written = 1;
end
end