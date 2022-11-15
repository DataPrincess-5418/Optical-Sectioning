function reconstructed_img = remove_integration_angles(img,angle)
  theta = 0:1:179;  
  [rd_data,xp_data] = radon(img,theta); 
  num_angles = size(rd_data,2);
  re_all_lines = rd_data;
  re_all_lines(:,max(angle-10,1):min(angle+10,179)) = 0.0;
  out_size = max(size(img));
  dtheta7 = theta(2) - theta(1);
  Recon_img = iradon(re_all_lines,dtheta7,out_size); 
  Recon_img_norm = (Recon_img - min(Recon_img(:)));
  Recon_img_norm1 = Recon_img_norm/(max(Recon_img_norm(:)) - min(Recon_img_norm(:)));
  reconstructed_img =  uint8(Recon_img_norm1*255);
end