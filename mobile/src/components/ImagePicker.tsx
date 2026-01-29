import React, { useState } from 'react';
import { View, Image, StyleSheet, Alert, ScrollView } from 'react-native';
import { Button, Card, IconButton, Text } from 'react-native-paper';
import * as ImagePickerLib from 'expo-image-picker';
import { Camera, Image as ImageIcon, X } from 'lucide-react-native';

interface ImagePickerProps {
  onImagesSelected: (images: string[]) => void;
  maxImages?: number;
  existingImages?: string[];
}

export const ImagePicker: React.FC<ImagePickerProps> = ({
  onImagesSelected,
  maxImages = 5,
  existingImages = [],
}) => {
  const [selectedImages, setSelectedImages] = useState<string[]>(existingImages);

  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePickerLib.requestCameraPermissionsAsync();
    const { status: libraryStatus } = await ImagePickerLib.requestMediaLibraryPermissionsAsync();

    if (cameraStatus !== 'granted' || libraryStatus !== 'granted') {
      Alert.alert(
        'Permissions Required',
        'Camera and photo library permissions are required to upload images.',
        [{ text: 'OK' }]
      );
      return false;
    }
    return true;
  };

  const handleTakePhoto = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    if (selectedImages.length >= maxImages) {
      Alert.alert('Limit Reached', `You can only upload up to ${maxImages} images.`);
      return;
    }

    const result = await ImagePickerLib.launchCameraAsync({
      mediaTypes: 'images',
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      const newImages = [...selectedImages, result.assets[0].uri];
      setSelectedImages(newImages);
      onImagesSelected(newImages);
    }
  };

  const handlePickFromGallery = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    if (selectedImages.length >= maxImages) {
      Alert.alert('Limit Reached', `You can only upload up to ${maxImages} images.`);
      return;
    }

    const result = await ImagePickerLib.launchImageLibraryAsync({
      mediaTypes: 'images',
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
      allowsMultipleSelection: true,
      selectionLimit: maxImages - selectedImages.length,
    });

    if (!result.canceled && result.assets.length > 0) {
      const newImages = [...selectedImages, ...result.assets.map((asset) => asset.uri)];
      setSelectedImages(newImages);
      onImagesSelected(newImages);
    }
  };

  const handleRemoveImage = (index: number) => {
    const newImages = selectedImages.filter((_, i) => i !== index);
    setSelectedImages(newImages);
    onImagesSelected(newImages);
  };

  return (
    <View style={styles.container}>
      <Text variant="titleMedium" style={styles.title}>
        Photos ({selectedImages.length}/{maxImages})
      </Text>

      <View style={styles.buttonContainer}>
        <Button
          mode="outlined"
          icon={() => <Camera size={20} color="#666" />}
          onPress={handleTakePhoto}
          style={styles.button}
          disabled={selectedImages.length >= maxImages}
        >
          Take Photo
        </Button>
        <Button
          mode="outlined"
          icon={() => <ImageIcon size={20} color="#666" />}
          onPress={handlePickFromGallery}
          style={styles.button}
          disabled={selectedImages.length >= maxImages}
        >
          Choose from Gallery
        </Button>
      </View>

      {selectedImages.length > 0 && (
        <ScrollView horizontal style={styles.imageScroll} showsHorizontalScrollIndicator={false}>
          {selectedImages.map((uri, index) => (
            <Card key={index} style={styles.imageCard}>
              <Image source={{ uri }} style={styles.image} />
              <IconButton
                icon={() => <X size={20} color="#fff" />}
                size={20}
                onPress={() => handleRemoveImage(index)}
                style={styles.removeButton}
                iconColor="#fff"
              />
            </Card>
          ))}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 16,
  },
  title: {
    marginBottom: 12,
    fontWeight: '600',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  button: {
    flex: 1,
  },
  imageScroll: {
    marginTop: 8,
  },
  imageCard: {
    width: 120,
    height: 120,
    marginRight: 12,
    borderRadius: 8,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  removeButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    margin: 0,
  },
});

export default ImagePicker;
