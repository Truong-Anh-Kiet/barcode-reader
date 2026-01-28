import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { scanBarcode } from '../services/api';
import { toast } from 'react-toastify';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

const ScanUploader = ({ onScanSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useWebcam, setUseWebcam] = useState(false);
  const [webcamReady, setWebcamReady] = useState(false);
  const [results, setResults] = useState(null);
  const webcamRef = useRef(null);

const handleCapture = async () => {
    let blob;
    let filename;

    if (useWebcam) {
      if (!webcamReady) {
        toast.error('Webcam not ready. Please allow camera access.');
        return;
      }
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;
      blob = await fetch(imageSrc).then(res => res.blob());
      filename = 'webcam.jpg';
    } else if (file) {
      blob = file;
      filename = file.name;
    } else {
      toast.error('Please select a file or use webcam');
      return;
    }

    setLoading(true);
    try {
      const data = await scanBarcode(blob);
      setResults(data);
      toast.success('Scan successful!');
      if (onScanSuccess) onScanSuccess();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Scan failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mb-12">
      <CardHeader>
        <CardTitle className="text-2xl">Scan Barcode</CardTitle>
        <CardDescription>Upload an image or use your webcam to scan barcodes</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex gap-4 items-center flex-wrap">
          <Button
            variant={useWebcam ? 'default' : 'outline'}
            onClick={() => setUseWebcam(!useWebcam)}
          >
            {useWebcam ? 'Switch to Upload' : 'Use Webcam'}
          </Button>

          {!useWebcam ? (
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-secondary file:text-secondary-foreground hover:file:bg-secondary/80"
            />
          ) : (
            <div className="w-full max-w-md mx-auto">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="w-full rounded-lg shadow-md"
                onUserMedia={() => setWebcamReady(true)}
                onUserMediaError={() => {
                  toast.error('Camera access denied');
                  setWebcamReady(false);
                }}
              />
            </div>
          )}
        </div>

        <Button
          onClick={handleCapture}
          disabled={loading || (!file && !useWebcam) || (useWebcam && !webcamReady)}
          size="lg"
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Scanning...
            </>
          ) : (
            'Scan Barcode'
          )}
        </Button>

        {results && (
          <div className="space-y-6 pt-6 border-t">
            <h3 className="text-xl font-semibold">Results ({results.count} detected)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.data.map((item, idx) => (
                <Card key={idx}>
                  <CardContent className="pt-6 space-y-3">
                    <p><strong>Content:</strong> {item.content}</p>
                    <p><strong>Type:</strong> {item.type || item.barcode_type}</p>
                    {item.image_url && (
                      <img src={item.image_url} alt="Original" className="w-full rounded-md shadow" loading="lazy" />
                    )}
                    {item.processed_image_url && (
                      <img src={item.processed_image_url} alt="Processed" className="w-full rounded-md shadow mt-4" loading="lazy" />
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ScanUploader;