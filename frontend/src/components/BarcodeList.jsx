import { useEffect, useState } from 'react';
import { getBarcodes, deleteBarcode , getUserInfo } from '../services/api';
import { toast } from 'react-toastify';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';

const BarcodeList = () => {
  const [barcodes, setBarcodes] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [selectedBarcode, setSelectedBarcode] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const itemsPerPage = 10;

  const fetchBarcodes = async (page = 1) => {
    setLoading(true);
    try {
      const { data, total } = await getBarcodes(itemsPerPage, (page - 1) * itemsPerPage);
      setBarcodes(data);
      setFiltered(data);
      setTotalPages(Math.ceil(total / itemsPerPage));
      setCurrentPage(page);
    } catch (err) {
      toast.error('Failed to load barcodes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarcodes();
  }, []);

  useEffect(() => {
    const filteredData = barcodes.filter(item =>
      item.content.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (!filterType || item.barcode_type === filterType)
    );
    setFiltered(filteredData);
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
    if (!window.confirm('Delete this barcode?')) return;
    try {
      await deleteBarcode(id);
      toast.success('Deleted');
      fetchBarcodes(currentPage);
    } catch {
      toast.error('Delete failed');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Barcode History</CardTitle>
        <div className="flex flex-col sm:flex-row gap-4 mt-4">
          <Input
            placeholder="Search content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="sm:max-w-xs"
          />
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="sm:w-48">
              <SelectValue placeholder="All types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All types</SelectItem>
              <SelectItem value="QR_CODE">QR Code</SelectItem>
              <SelectItem value="CODE_128">Code 128</SelectItem>
              {/* Thêm type khác nếu cần */}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 class loading h-8 w-8 animate-spin />
          </div>
        ) : (
          <>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Content</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.content}</TableCell>
                      <TableCell>{item.barcode_type}</TableCell>
                      <TableCell>{new Date(item.created_at).toLocaleString()}</TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button size="sm" onClick={() => setSelectedBarcode(item)}>View</Button>
                        {currentUser?.is_superuser && (
                          <Button size="sm" variant="destructive" onClick={() => handleDelete(item.id)}>
                            Delete
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {totalPages > 1 && (
              <Pagination className="mt-6">
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() => fetchBarcodes(currentPage - 1)}
                      className={currentPage === 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>
                  {[...Array(totalPages)].map((_, i) => (
                    <PaginationItem key={i}>
                      <PaginationLink
                        onClick={() => fetchBarcodes(i + 1)}
                        isActive={currentPage === i + 1}
                        className="cursor-pointer"
                      >
                        {i + 1}
                      </PaginationLink>
                    </PaginationItem>
                  ))}
                  <PaginationItem>
                    <PaginationNext
                      onClick={() => fetchBarcodes(currentPage + 1)}
                      className={currentPage === totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            )}
          </>
        )}

        <Dialog open={!!selectedBarcode} onOpenChange={() => setSelectedBarcode(null)}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Barcode Detail</DialogTitle>
            </DialogHeader>
            {selectedBarcode && (
              <div className="space-y-4">
                <div><strong>ID:</strong> {selectedBarcode.id}</div>
                <div><strong>Content:</strong> {selectedBarcode.content}</div>
                <div><strong>Type:</strong> {selectedBarcode.barcode_type}</div>
                <div><strong>Created:</strong> {new Date(selectedBarcode.created_at).toLocaleString()}</div>
                {selectedBarcode.image_url && (
                  <img src={selectedBarcode.image_url} alt="Original" className="w-full rounded-lg shadow" />
                )}
                {selectedBarcode.processed_image_url && (
                  <img src={selectedBarcode.processed_image_url} alt="Processed" className="w-full rounded-lg shadow mt-4" />
                )}
              </div>
            )}
            <DialogFooter>
              <Button variant="secondary" onClick={() => setSelectedBarcode(null)}>Close</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default BarcodeList;