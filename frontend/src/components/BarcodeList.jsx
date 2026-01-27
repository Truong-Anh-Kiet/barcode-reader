import { useEffect, useState } from 'react';
import Modal from 'react-modal';
import ReactPaginate from 'react-paginate';
import { getBarcodes, deleteBarcode } from '../services/api';
import { toast } from 'react-toastify';

Modal.setAppElement('#root');

const BarcodeList = () => {
  const [barcodes, setBarcodes] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedBarcode, setSelectedBarcode] = useState(null);
  const itemsPerPage = 10;
  const fetchBarcodes = async () => {
    setLoading(true);
    try {
      const { data, total } = await getBarcodes(itemsPerPage, currentPage * itemsPerPage);
      setBarcodes(data);
      setTotalCount(total);
    } catch (err) {
      setError('Failed to load list');
      toast.error('Failed to load barcode list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarcodes();
  }, [currentPage]);

  useEffect(() => {
    let filtered = barcodes.filter((item) => 
      item.content.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (filterType ? item.barcode_type === filterType : true)
    );
    setFilteredBarcodes(filtered);
  }, [searchTerm, filterType, barcodes]);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getUserInfo();
        setCurrentUser(data);
      } catch {}
    };
    fetchUser();
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteBarcode(id);
      toast.success('Delete successful');
      fetchBarcodes();
    } catch (err) {
      toast.error('Delete failed');
    }
  };

  const handlePageChange = (data) => {
    setCurrentPage(data.selected);
  };

  const pageCount = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Saved Barcodes List</h2>
        <button onClick={fetchBarcodes} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Refresh
        </button>
      </div>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Find by content..."
          className="px-4 py-2 border rounded-md flex-1"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border rounded-md"
        >
          <option value="">All Types</option>
          <option value="EAN13">EAN13</option>
          <option value="QR_CODE">QR Code</option>
        </select>
      </div>
      {loading && <p className="text-center text-gray-500">Loading...</p>}
      {error && <p className="text-red-600 text-center mb-4">{error}</p>}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {barcodes.map((item) => (
              <tr key={item.id}>
                <td className="px-6 py-4 whitespace-nowrap">{item.id}</td>
                <td className="px-6 py-4 whitespace-nowrap">{item.content}</td>
                <td className="px-6 py-4 whitespace-nowrap">{item.barcode_type}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {item.image_url && (
                    <img src={item.image_url} alt="Original" className="w-20 h-20 object-cover rounded shadow" />
                  )}
                  {item.processed_image_url && (
                    <img src={item.processed_image_url} alt="Processed barcode" className="w-20 h-20 object-cover rounded shadow mt-2" loading="lazy" />
                  )}
                  <button onClick={() => setSelectedBarcode(item)} className="text-blue-600 hover:underline mr-4">Detail</button>
                  {!loadingUser && currentUser?.is_superuser && (
                    <button onClick={() => handleDelete(item.id)} className="text-red-600 hover:underline">Delete</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ReactPaginate
        previousLabel="Before"
        nextLabel="After"
        breakLabel="..."
        pageCount={pageCount}
        marginPagesDisplayed={2}
        pageRangeDisplayed={5}
        onPageChange={handlePageChange}
        containerClassName="flex justify-center mt-6 space-x-2"
        pageClassName="bg-white px-4 py-2 border rounded cursor-pointer"
        activeClassName="bg-blue-600 text-white"
      />
      <Modal
        isOpen={!!selectedBarcode}
        onRequestClose={() => setSelectedBarcode(null)}
        className="bg-white p-8 rounded-lg shadow-lg max-w-md mx-auto mt-20"
        overlayClassName="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      >
        {selectedBarcode && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Detail Barcode</h2>
            <p><strong>ID:</strong> {selectedBarcode.id}</p>
            <p><strong>Content:</strong> {selectedBarcode.content}</p>
            <p><strong>Type:</strong> {selectedBarcode.barcode_type}</p>
            <p><strong>Created At:</strong> {new Date(selectedBarcode.created_at).toLocaleString()}</p>
            {selectedBarcode.image_url && (
              <div className="mt-4">
                <p className="font-semibold mb-2">Original Image:</p>
                <img
                  src={selectedBarcode.image_url}
                  alt="Original barcode"
                  className="max-w-full rounded shadow-lg"
                  loading="lazy"
                />
              </div>
            )}

            {selectedBarcode.processed_image_url && (
              <div className="mt-4">
                <p className="font-semibold mb-2">Processed Image:</p>
                <img
                  src={selectedBarcode.processed_image_url}
                  alt="Processed barcode"
                  className="max-w-full rounded shadow-lg"
                  loading="lazy"
                />
              </div>
            )}
            <button onClick={() => setSelectedBarcode(null)} className="mt-4 bg-red-600 text-white px-4 py-2 rounded">
              Close
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BarcodeList;