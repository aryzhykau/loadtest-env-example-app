import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Box,
  Button,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import { PlayArrow as PlayIcon } from '@mui/icons-material';
import { createTask, getTaskStatus } from '../services/api';
import type { TaskCreate, TaskResponse } from '../types/api';

export default function TaskRunner() {
  const [taskType, setTaskType] = useState('process_data');
  const [params, setParams] = useState<Record<string, any>>({});
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [polling, setPolling] = useState(false);

  const createTaskMutation = useMutation({
    mutationFn: (task: TaskCreate) => createTask(task),
    onSuccess: (data) => {
      setCurrentTask(data);
      startPolling(data.task_id);
    },
  });

  const startPolling = (taskId: string) => {
    setPolling(true);
    const interval = setInterval(async () => {
      try {
        const status = await getTaskStatus(taskId);
        setCurrentTask(status);
        
        if (status.status === 'success' || status.status === 'failure') {
          setPolling(false);
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Failed to get task status:', error);
        setPolling(false);
        clearInterval(interval);
      }
    }, 2000);
  };

  const handleRunTask = () => {
    const taskData: TaskCreate = {
      task_type: taskType,
      params: params,
    };
    createTaskMutation.mutate(taskData);
  };

  const renderTaskParams = () => {
    switch (taskType) {
      case 'process_data':
        return (
          <>
            <TextField
              label="Data ID"
              fullWidth
              value={params.data_id || ''}
              onChange={(e) => setParams({ ...params, data_id: e.target.value })}
            />
            <TextField
              label="Processing Time (seconds)"
              type="number"
              fullWidth
              value={params.processing_time || 5}
              onChange={(e) =>
                setParams({ ...params, processing_time: parseInt(e.target.value) })
              }
            />
          </>
        );
      case 'generate_report':
        return (
          <>
            <FormControl fullWidth>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={params.report_type || 'summary'}
                label="Report Type"
                onChange={(e) =>
                  setParams({ ...params, report_type: e.target.value })
                }
              >
                <MenuItem value="summary">Summary</MenuItem>
                <MenuItem value="detailed">Detailed</MenuItem>
                <MenuItem value="analytics">Analytics</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      case 'simulate_load':
        return (
          <>
            <TextField
              label="Duration (seconds)"
              type="number"
              fullWidth
              value={params.duration || 10}
              onChange={(e) =>
                setParams({ ...params, duration: parseInt(e.target.value) })
              }
            />
            <FormControl fullWidth>
              <InputLabel>Intensity</InputLabel>
              <Select
                value={params.intensity || 'medium'}
                label="Intensity"
                onChange={(e) =>
                  setParams({ ...params, intensity: e.target.value })
                }
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      default:
        return null;
    }
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'success' | 'error' => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'started':
        return 'primary';
      case 'success':
        return 'success';
      case 'failure':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Task Runner
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Run a Task
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <FormControl fullWidth>
            <InputLabel>Task Type</InputLabel>
            <Select
              value={taskType}
              label="Task Type"
              onChange={(e) => {
                setTaskType(e.target.value);
                setParams({});
              }}
            >
              <MenuItem value="process_data">Process Data</MenuItem>
              <MenuItem value="generate_report">Generate Report</MenuItem>
              <MenuItem value="simulate_load">Simulate Load</MenuItem>
            </Select>
          </FormControl>

          {renderTaskParams()}

          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleRunTask}
            disabled={createTaskMutation.isPending || polling}
            fullWidth
          >
            Run Task
          </Button>
        </Box>
      </Paper>

      {currentTask && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Task Status</Typography>
              <Chip
                label={currentTask.status}
                color={getStatusColor(currentTask.status)}
              />
            </Box>

            {polling && <LinearProgress sx={{ mb: 2 }} />}

            <Typography variant="body2" color="textSecondary" gutterBottom>
              Task ID: {currentTask.task_id}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Type: {currentTask.task_type}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Created: {new Date(currentTask.created_at).toLocaleString()}
            </Typography>

            {currentTask.result && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Result:
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                  <pre style={{ margin: 0, fontSize: '12px' }}>
                    {JSON.stringify(currentTask.result, null, 2)}
                  </pre>
                </Paper>
              </Box>
            )}

            {currentTask.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {currentTask.error}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
