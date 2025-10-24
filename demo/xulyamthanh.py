
import numpy as np
import librosa
import soundfile as sf
import argparse




def mix_audio(input_path1, input_path2, output_path, volume1, volume2):
    """
    Hàm này nhận vào đường dẫn của 2 file âm thanh, trộn chúng lại
    và lưu kết quả vào một file mới.
    """
    try:
       
        print(f"Đang đọc file 1: {input_path1}...")
        data1, sr1 = librosa.load(input_path1, sr=None)
        
        print(f"Đang đọc file 2: {input_path2}...")
        data2, sr2 = librosa.load(input_path2, sr=None)

        
        if sr1 != sr2:
            print(f"Cảnh báo: Tần số lấy mẫu khác nhau ({sr1}Hz và {sr2}Hz). Đang chuyển file 2 về {sr1}Hz.")
           
            data2 = librosa.resample(y=data2, orig_sr=sr2, target_sr=sr1)

        
        len1, len2 = len(data1), len(data2)
        if len1 > len2:
            
            padding = np.zeros(len1 - len2)
            data2 = np.concatenate((data2, padding))
        elif len2 > len1:
     
            padding = np.zeros(len2 - len1)
            data1 = np.concatenate((data1, padding))

      
        print("Đang trộn âm thanh...")
        mixed_data = (data1 * volume1) + (data2 * volume2)

       
        max_abs_val = np.max(np.abs(mixed_data))
        if max_abs_val > 1.0:
            mixed_data = mixed_data / max_abs_val
            print("Thông báo: Âm thanh đã được chuẩn hóa để tránh vỡ tiếng.")

      
        sf.write(output_path, mixed_data, sr1)
        print(f"✅ Hoàn thành! File trộn đã được lưu tại: {output_path}")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")



if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(description="Một công cụ đơn giản để trộn hai file âm thanh.")

  
    parser.add_argument("input_file1", help="Đường dẫn đến file âm thanh thứ nhất.")
    parser.add_argument("input_file2", help="Đường dẫn đến file âm thanh thứ hai.")
    parser.add_argument("output_file", help="Tên file để lưu kết quả (ví dụ: ket_qua.wav).")

   
    parser.add_argument("--vol1", type=float, default=1.0, help="Âm lượng của file 1. Mặc định: 1.0")
    parser.add_argument("--vol2", type=float, default=1.0, help="Âm lượng của file 2. Mặc định: 1.0")
    

    args = parser.parse_args()
    
   
    mix_audio(args.input_file1, args.input_file2, args.output_file, args.vol1, args.vol2)