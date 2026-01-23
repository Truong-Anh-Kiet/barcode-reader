import React, { useEffect, useState } from 'react';
import ReactPaginate from 'react-paginate';
import { getBarcodes, deleteBarcode } from '../services/api';

const BarcodeList = () => {
  const [barcodes, setBarcodes] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const itemsPerPage = 10;
  const fetchBarcodes = async () => {
    setLoading(true);
    try {
      const { data, total } = await getBarcodes(itemsPerPage, currentPage * itemsPerPage);
      setBarcodes(data);
      setTotalCount(total);
    } catch (err) {
      setError('Failed to load list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarcodes();
  }, [currentPage]);

  const handleDelete = async (id) => {
    try {
      await deleteBarcode(id);
      fetchBarcodes();
    } catch (err) {
      setError('Delete failed');
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
                  <button onClick={() => handleDelete(item.id)} className="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pageCount > 1 && (
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
          previousClassName="bg-white px-4 py-2 border rounded cursor-pointer"
          nextClassName="bg-white px-4 py-2 border rounded cursor-pointer"
        />
      )}
    </div>
  );
};

export default BarcodeList;