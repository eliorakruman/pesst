import torchvision.transforms as transforms
from torch.utils.data import TensorDataset, DataLoader
from net_utils import *
import os
from PIL import Image
import pillow_heif
import cv2

RUNWITHLOG: bool = False


def load_data():
    pillow_heif.register_heif_opener()
    classifications = os.listdir("./DataSets/")
    transform = transforms.Compose([
        transforms.PILToTensor()
    ])
    image_data = []
    classification_data = []
    class_encoding: int = 0
    for classification in classifications:
        path = f"./DataSets/{classification}"
        for file in os.listdir(path):
            img_tensor = transform(Image.open(f"{path}/{file}"))
            image_data.append(img_tensor.type(torch.FloatTensor))
            classification_data.append(class_encoding)
        class_encoding += 1
    dataset = TensorDataset(torch.tensor(torch.stack(image_data)), torch.tensor(classification_data))
    train_loader: DataLoader = DataLoader(dataset, batch_size=20, shuffle=True)
    test_loader: DataLoader = DataLoader(dataset, batch_size=20, shuffle=True)
    return train_loader, test_loader


def train(train_loader: DataLoader, net, loss_function, optimizer, epoch_num):
    # loops over input and expected values sampled from train_loader
    running_loss: float = 0.0
    net.train()
    for batch, data in enumerate(train_loader, 0):
        input_vals, expected = data
        optimizer.zero_grad()
        outputs = net(input_vals)
        loss = loss_function(outputs, expected)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        if batch % 100 == 0 and batch != 0 and RUNWITHLOG:
            print(f'[{epoch_num + 1}, {batch + 1}] loss: {running_loss / 100:.3f}')
            running_loss = 0.0
    print('Finished Training')


def test(test_loader: DataLoader, net, epoch_num: int):
    net.eval()
    accuracy = 0

    with torch.no_grad():
        for features, true_labels in test_loader:
            predictions = net(features)
            predictions = torch.max(predictions, 1)[1].data.squeeze()
            accuracy = (predictions == true_labels).sum().item() / float(true_labels.size(0))
    if RUNWITHLOG:
        print(f"Accuracy at Epoch {epoch_num + 1}: {accuracy*100}%")


if __name__ == '__main__':
    epochs: int = 1
    train_data, test_data = load_data()

    net = Net()
    loss_function = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), 0.001)
    # outer loop for multiple training epochs
    for epoch in range(epochs):
        train(train_data, net, loss_function, optimizer, epoch)
        test(test_data, net, epoch)

