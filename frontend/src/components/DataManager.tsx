import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import {
  listDataEntries,
  createDataEntry,
  updateDataEntry,
  deleteDataEntry,
} from '../services/api';
import type { DataEntry, DataEntryCreate, DataEntryUpdate } from '../types/api';

export default function DataManager() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<DataEntry | null>(null);
  const [formData, setFormData] = useState<DataEntryCreate>({
    name: '',
    description: '',
    value: 0,
    status: 'active',
  });

  const { data: entries, isLoading, error } = useQuery({
    queryKey: ['dataEntries'],
    queryFn: () => listDataEntries(),
  });

  const createMutation = useMutation({
    mutationFn: createDataEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataEntries'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
      handleClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: DataEntryUpdate }) =>
      updateDataEntry(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataEntries'] });
      handleClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDataEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataEntries'] });
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
  });

  const handleOpen = (entry?: DataEntry) => {
    if (entry) {
      setEditingEntry(entry);
      setFormData({
        name: entry.name,
        description: entry.description,
        value: entry.value,
        status: entry.status,
      });
    } else {
      setEditingEntry(null);
      setFormData({ name: '', description: '', value: 0, status: 'active' });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingEntry(null);
  };

  const handleSubmit = () => {
    if (editingEntry) {
      updateMutation.mutate({ id: editingEntry._id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Failed to load data entries</Alert>;
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Data Manager</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          Add Entry
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Value</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries?.map((entry) => (
              <TableRow key={entry._id}>
                <TableCell>{entry.name}</TableCell>
                <TableCell>{entry.description || '-'}</TableCell>
                <TableCell align="right">{entry.value}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.status}
                    color={entry.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpen(entry)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => deleteMutation.mutate(entry._id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingEntry ? 'Edit Entry' : 'Create Entry'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
            />
            <TextField
              label="Value"
              type="number"
              fullWidth
              value={formData.value}
              onChange={(e) =>
                setFormData({ ...formData, value: parseFloat(e.target.value) })
              }
            />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                label="Status"
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    status: e.target.value as 'active' | 'inactive' | 'archived',
                  })
                }
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="archived">Archived</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingEntry ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
