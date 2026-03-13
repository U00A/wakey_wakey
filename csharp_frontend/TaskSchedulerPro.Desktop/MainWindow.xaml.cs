using System;
using System.Collections.ObjectModel;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using System.Windows;

namespace TaskSchedulerPro.Desktop;

public partial class MainWindow : Window
{
    private readonly HttpClient _httpClient = new() { BaseAddress = new Uri("http://127.0.0.1:8000/") };

    public ObservableCollection<TaskDto> Tasks { get; } = new();

    public MainWindow()
    {
        InitializeComponent();
        TasksGrid.ItemsSource = Tasks;
        _ = LoadTasksAsync();
    }

    private async Task LoadTasksAsync()
    {
        try
        {
            StatusTextBlock.Text = "Loading tasks...";
            Tasks.Clear();

            var tasks = await _httpClient.GetFromJsonAsync<TaskDto[]>("tasks");
            if (tasks != null)
            {
                foreach (var t in tasks)
                {
                    Tasks.Add(t);
                }
            }

            StatusTextBlock.Text = $"Loaded {Tasks.Count} task(s).";
        }
        catch (Exception ex)
        {
            StatusTextBlock.Text = "Failed to load tasks.";
            MessageBox.Show(this, ex.Message, "Error loading tasks", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private async void Refresh_Click(object sender, RoutedEventArgs e)
    {
        await LoadTasksAsync();
    }

    private async void AddTask_Click(object sender, RoutedEventArgs e)
    {
        var title = NewTaskTitleTextBox.Text?.Trim();
        if (string.IsNullOrWhiteSpace(title))
        {
            MessageBox.Show(this, "Please enter a task title.", "Validation", MessageBoxButton.OK, MessageBoxImage.Information);
            return;
        }

        try
        {
            StatusTextBlock.Text = "Creating task...";

            var newTask = new TaskCreateDto
            {
                Title = title,
                Priority = "Medium",
                Category = "Personal"
            };

            var response = await _httpClient.PostAsJsonAsync("tasks", newTask);
            response.EnsureSuccessStatusCode();

            var created = await response.Content.ReadFromJsonAsync<TaskDto>();
            if (created != null)
            {
                Tasks.Add(created);
                NewTaskTitleTextBox.Text = string.Empty;
                StatusTextBlock.Text = "Task created.";
            }
            else
            {
                StatusTextBlock.Text = "Task created, but response was empty.";
            }
        }
        catch (Exception ex)
        {
            StatusTextBlock.Text = "Failed to create task.";
            MessageBox.Show(this, ex.Message, "Error creating task", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }
}

public sealed class TaskDto
{
    public int Id { get; set; }
    public string Title { get; set; } = "";
    public string? Description { get; set; }
    public string Priority { get; set; } = "Medium";
    public string Category { get; set; } = "Personal";
    public string Status { get; set; } = "Pending";
    public string? DueDate { get; set; }
    public string? ReminderTime { get; set; }
}

public sealed class TaskCreateDto
{
    public string Title { get; set; } = "";
    public string? Description { get; set; }
    public string Priority { get; set; } = "Medium";
    public string Category { get; set; } = "Personal";
    public string? DueDate { get; set; }
    public string? ReminderTime { get; set; }
    public string RecurringType { get; set; } = "None";
    public int RecurringInterval { get; set; } = 1;
}

