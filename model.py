import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import os
import cv2
import numpy as np

# Custom Dataset Class
class SatelliteImageDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.transform = transform
        self.image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.jpg')])

    def __len__(self):
        return len(self.image_files) - 2

    def __getitem__(self, idx):
        img1 = cv2.imread(self.image_files[idx])
        img2 = cv2.imread(self.image_files[idx + 1])
        img3 = cv2.imread(self.image_files[idx + 2])

        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)
            img3 = self.transform(img3)

        return img1, img2, img3

# Transformations
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# Load dataset
image_folder = '/content/drive/MyDrive/images'  # Update with your image folder path
dataset = SatelliteImageDataset(image_folder, transform=transform)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=4)

# Define Super SloMo Model (simplified version)
class SuperSloMo(nn.Module):
    def __init__(self):
        super(SuperSloMo, self).__init__()
        self.conv1 = nn.Conv2d(6, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(64, 3, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, frame1, frame2):
        x = torch.cat((frame1, frame2), dim=1)
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        interpolated_frame = self.conv4(x)
        return interpolated_frame

# Initialize model, loss function, and optimizer
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SuperSloMo().to(device)
criterion = nn.L1Loss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# Training loop
num_epochs = 50

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for i, (frame_t1, frame_t, frame_t2) in enumerate(dataloader):
        frame_t1, frame_t, frame_t2 = frame_t1.to(device), frame_t.to(device), frame_t2.to(device)

        optimizer.zero_grad()

        interpolated_frame = model(frame_t1, frame_t2)

        loss = criterion(interpolated_frame, frame_t)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(dataloader):.4f}")

print("Training complete!")

# Save the trained model
model_path = 'super_slo_mo.pth'
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")
