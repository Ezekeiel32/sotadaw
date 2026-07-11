/* ------------------------------------------------------------
name: "shakuhachi"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Shakuhachi -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Shakuhachi_H__
#define  __Shakuhachi_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Shakuhachi
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class ShakuhachiSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec6[2];
	
  public:
	
	int getNumInputsShakuhachiSIG0() {
		return 0;
	}
	int getNumOutputsShakuhachiSIG0() {
		return 1;
	}
	
	void instanceInitShakuhachiSIG0(int sample_rate) {
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iVec2[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec6[l9] = 0;
		}
	}
	
	void fillShakuhachiSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec6[0] = (iVec2[1] + iRec6[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec6[0]));
			iVec2[1] = iVec2[0];
			iRec6[1] = iRec6[0];
		}
	}

};

static ShakuhachiSIG0* newShakuhachiSIG0() { return (ShakuhachiSIG0*)new ShakuhachiSIG0(); }
static void deleteShakuhachiSIG0(ShakuhachiSIG0* dsp) { delete dsp; }

static float Shakuhachi_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0ShakuhachiSIG0[65536];

class Shakuhachi : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider0;
	int iRec1[2];
	FAUSTFLOAT fHslider1;
	float fRec2[2];
	FAUSTFLOAT fHslider2;
	float fConst4;
	FAUSTFLOAT fHslider3;
	float fConst6;
	float fConst8;
	float fConst10;
	FAUSTFLOAT fHslider4;
	float fConst11;
	int iRec5[2];
	float fRec4[3];
	float fRec3[3];
	float fConst12;
	FAUSTFLOAT fHslider5;
	float fConst13;
	float fRec8[2];
	FAUSTFLOAT fHslider6;
	FAUSTFLOAT fHslider7;
	float fConst14;
	float fRec7[2];
	float fRec9[2];
	FAUSTFLOAT fHslider8;
	
 public:
	Shakuhachi() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Shakuhachi -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "shakuhachi.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "shakuhachi");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		ShakuhachiSIG0* sig0 = newShakuhachiSIG0();
		sig0->instanceInitShakuhachiSIG0(sample_rate);
		sig0->fillShakuhachiSIG0(65536, ftbl0ShakuhachiSIG0);
		deleteShakuhachiSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.003f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 1.0f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst4 = 0.2f / std::max<float>(1.0f, 0.15f * fConst0);
		float fConst5 = std::tan(23561.945f / fConst0);
		fConst6 = 2.0f * (1.0f - 1.0f / Shakuhachi_faustpower2_f(fConst5));
		float fConst7 = 1.0f / fConst5;
		fConst8 = (fConst7 + -1.4142135f) / fConst5 + 1.0f;
		float fConst9 = (fConst7 + 1.4142135f) / fConst5 + 1.0f;
		fConst10 = 1.0f / fConst9;
		fConst11 = 4.712389f / fConst0;
		fConst12 = 0.6f / fConst9;
		fConst13 = 1.0f / fConst0;
		fConst14 = 2.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(0.25f);
		fHslider2 = FAUSTFLOAT(0.05f);
		fHslider3 = FAUSTFLOAT(0.45f);
		fHslider4 = FAUSTFLOAT(4.4e+02f);
		fHslider5 = FAUSTFLOAT(4.5f);
		fHslider6 = FAUSTFLOAT(0.01f);
		fHslider7 = FAUSTFLOAT(0.0f);
		fHslider8 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec5[l5] = 0;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec7[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec9[l12] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Shakuhachi* clone() {
		return new Shakuhachi();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("shakuhachi");
		ui_interface->addHorizontalSlider("attack", &fHslider2, FAUSTFLOAT(0.05f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bend", &fHslider7, FAUSTFLOAT(0.0f), FAUSTFLOAT(-0.06f), FAUSTFLOAT(0.06f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("breath", &fHslider3, FAUSTFLOAT(0.45f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.8f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("muraiki", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("release", &fHslider1, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider5, FAUSTFLOAT(4.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(7.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider6, FAUSTFLOAT(0.01f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		int iSlow2 = fSlow0 == 0.0f;
		float fSlow3 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fHslider3);
		float fSlow7 = float(fHslider4);
		float fSlow8 = std::tan(fConst11 * fSlow7);
		float fSlow9 = 2.0f * (1.0f - 1.0f / Shakuhachi_faustpower2_f(fSlow8));
		float fSlow10 = 1.0f / fSlow8;
		float fSlow11 = (fSlow10 + -0.5f) / fSlow8 + 1.0f;
		float fSlow12 = (fSlow10 + 0.5f) / fSlow8 + 1.0f;
		float fSlow13 = 1.0f / fSlow12;
		float fSlow14 = 1.0f / (fSlow8 * fSlow12);
		float fSlow15 = fConst13 * float(fHslider5);
		float fSlow16 = float(fHslider6);
		float fSlow17 = fSlow7 * (float(fHslider7) + 1.0f);
		float fSlow18 = fConst14 * fSlow17;
		float fSlow19 = fConst13 * fSlow17;
		float fSlow20 = 0.6f * float(fHslider8);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			iRec1[0] = iSlow2 * (iRec1[1] + 1);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec0[1] >= fSlow0);
			float fTemp1 = std::max<float>(0.0f, std::min<float>(fSlow5 * fRec2[0], std::max<float>(fConst4 * (fSlow4 - fRec2[0]) + 1.0f, 0.8f)) * (1.0f - fSlow3 * float(iRec1[0])));
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			fRec4[0] = 4.656613e-10f * float(iRec5[0]) - fSlow13 * (fSlow11 * fRec4[2] + fSlow9 * fRec4[1]);
			fRec3[0] = fSlow14 * (fRec4[0] - fRec4[2]) - fConst10 * (fConst8 * fRec3[2] + fConst6 * fRec3[1]);
			int iTemp2 = 1 - iVec1[1];
			float fTemp3 = ((iTemp2) ? 0.0f : fSlow15 + fRec8[1]);
			fRec8[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = fSlow16 * ftbl0ShakuhachiSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 1.0f;
			float fTemp5 = ((iTemp2) ? 0.0f : fRec7[1] + fSlow18 * fTemp4);
			fRec7[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp2) ? 0.0f : fRec9[1] + fSlow19 * fTemp4);
			fRec9[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = fSlow20 * (0.7f * (ftbl0ShakuhachiSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + 0.2f * ftbl0ShakuhachiSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))]) * fTemp1 + fConst12 * (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) * (fSlow6 * fTemp1 + fSlow1 * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fConst3 * (fConst1 - fTemp0) + 1.0f))));
			output0[i0] = FAUSTFLOAT(fTemp7);
			output1[i0] = FAUSTFLOAT(fTemp7);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			iRec5[1] = iRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec8[1] = fRec8[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
		}
	}

};

#endif
