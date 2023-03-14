from getdata import get_data
from train import train, validate
# from utils import resnet18 as rn
# from utils import dropout_model as dm
# from utils import focuseddropout_model as fm
# from utils import antifdo_model as afm
from utils.vgg16 import VGG
from utils import vgg16_dropout as vd
from utils import vgg16_focuseddropout as vfd
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from plotting import plot

##########################################Load Model & Data##################################################
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

############# ResNet
# model = rn.ResNet18(num_classes = 100)
# model_name = "resnet18_cifar100"

############# ResNet with dropout
# model = dm.ResNet18(num_classes = 100, p = 0.2) #0.2 Dropout rate
# model_name = "resnet18_cifar100_dropout0.2"

# model = dm.ResNet18(num_classes = 100, p = 0.5) #0.5 Dropout rate
# model_name = "resnet18_cifar100_dropout0.5"

############# ResNet with FocusedDropout
# model = fm.ResNet18(num_classes = 100, par_rate = 0.01) #0.01 FocusedDropout participation rate
# model_name = "resnet18_cifar100_focuseddropout0.01sgd"

# model = fm.ResNet18(num_classes = 100, par_rate = 0.05) #0.05 FocusedDropout participation rate
# model_name = "resnet18_cifar100_focuseddropout0.05sgd"

############# VGG16
# model = VGG('VGG16', num_classes = 100)
# model_name = "vgg16_cifar100"

# ############# VGG16 with Dropout
# model = vd.VGG('VGG16', num_classes = 100)
# model_name = "cifar100/vgg/vgg16_cifar100_dropout0.2"

# ############# VGG16 with FocusedDropout
model = vfd.VGG('VGG16', num_classes = 100)
model_name = "cifar100/vgg/vgg16_cifar100_focuseddropout0.1"

filename = "models/" + model_name + '.pth'
# model = pickle.load(open(filename, "rb"))
########################################Train & Validate#####################################################
epochs = 300
train_loader, valid_loader = get_data(batch_size=128)

model.to(device)
loss = nn.CrossEntropyLoss()
loss.to(device)

optimizer = optim.SGD(model.parameters(), lr=0.01,
                      momentum=0.9, weight_decay=5e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=200)

train_losses, train_accs, val_losses, val_accs = [], [], [], []

for _ in range(epochs):
    print(f"Epoch {_}")
    train_loss, train_acc = train(model, train_loader, optimizer, loss, device)
    train_losses.append(train_loss)
    train_accs.append(train_acc)
    
    val_loss, val_acc = validate(model, valid_loader, loss, device)
    val_losses.append(val_loss)
    val_accs.append(val_acc)
    
    scheduler.step()
    print(f"Training loss: {train_loss}, Training accuracy: {train_acc}")
    print(f"Validation loss: {val_loss}, Validation accuracy: {val_acc}")
    
print("Training Done!")
print("Best training accuracy: ", max(train_accs))
print("Best validation accuracy: ", max(val_accs))
plot(train_losses, train_accs, val_losses, val_accs, model_name)

# Save Model
torch.save(model.state_dict(), filename)
# torch.save(model, filename)
# pickle.dump(model, open(filename, "wb"))
print(f"Model saved on {filename}")