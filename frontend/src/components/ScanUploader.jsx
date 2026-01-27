import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { scanBarcode } from '../services/api';
import { toast } from 'react-toastify';

const ScanUploader = ({ onScanSuccess }) => {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [useWebcam, setUseWebcam] = useState(false);
  const webcamRef = useRef(null);

const handleCapture = async () => {
    if (useWebcam) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
      toast.error('Cannot capture image from webcam. Check camera permissions.');
      return;
    }
      const blob = await fetch(imageSrc).then((res) => res.blob());
      await performScan(blob, 'webcam.jpg');
    } else if (file) {
      await performScan(file, file.name);
    } else {
      toast.error('Please select a file or use the webcam');
    }
  };

const performScan = async (fileBlob, filename) => {
    setLoading(true);
    setError('');
    try {
      const data = await scanBarcode(fileBlob);
      setResults(data);
      toast.success('Scan successful!');
      if (onScanSuccess) onScanSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed');
      toast.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md mb-12">
      <h2 className="text-2xl font-semibold mb-6">Scan Barcode</h2>
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => setUseWebcam(!useWebcam)}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          {useWebcam ? 'Switch to Upload File' : 'Use Webcam'}
        </button>
        {!useWebcam ? (
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        ) : (
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="rounded shadow-md"
          />
        )}
        <button
          onClick={handleCapture}
          disabled={loading}
          className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </div>
      {error && <p className="text-red-600 font-medium mb-4">{error}</p>}
      {results && (
        <div>
          <h3 className="text-xl font-semibold mb-4">Detected {results.count} Barcode</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.data.map((item, idx) => (
              <div key={idx} className="bg-gray-50 p-6 rounded-lg shadow">
                <p><strong>Content:</strong> {item.content}</p>
                <p><strong>Type:</strong> {item.type}</p>
                {item.image_url && <img src={item.image_url} alt="Original" className="mt-4 rounded shadow w-full object-cover" loading="lazy" />}
                {item.processed_image_url && <img src={item.processed_image_url} alt="Processed" className="mt-2 rounded shadow w-full object-cover" loading="lazy" />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanUploader;